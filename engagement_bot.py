import time
import sys
import random
import json
import requests
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from config import (
    META_PAGE_ACCESS_TOKEN,
    INSTAGRAM_ACCOUNT_ID,
    FACEBOOK_PAGE_ID,
    THREADS_USER_ID,
    THREADS_ACCESS_TOKEN,
    COMMENT_CHECK_INTERVAL_MINUTES,
    BRAND
)
from content_engine import call_gemini
from notifier import send_telegram_alert

BASE_DIR = Path(__file__).resolve().parent
REPLIED_COMMENTS_FILE = BASE_DIR / "replied_comments.json"

GRAPH_VERSION = "v21.0"
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"
THREADS_URL = "https://graph.threads.net/v1.0"

class EngagementBot:
    def __init__(self):
        self.page_token = str(META_PAGE_ACCESS_TOKEN or "").strip()
        self.ig_account_id = str(INSTAGRAM_ACCOUNT_ID or "").strip()
        self.fb_page_id = str(FACEBOOK_PAGE_ID or "").strip()
        self.threads_user_id = str(THREADS_USER_ID or "").strip()
        self.threads_token = str(THREADS_ACCESS_TOKEN or "").strip()
        self.interval_minutes = COMMENT_CHECK_INTERVAL_MINUTES
        self.replied_comment_ids = self._load_replied_ids()

    def _load_replied_ids(self) -> set:
        if REPLIED_COMMENTS_FILE.exists():
            try:
                with open(REPLIED_COMMENTS_FILE, "r", encoding="utf-8") as f:
                    return set(json.load(f))
            except Exception:
                return set()
        return set()

    def _save_replied_ids(self):
        try:
            with open(REPLIED_COMMENTS_FILE, "w", encoding="utf-8") as f:
                json.dump(list(self.replied_comment_ids), f, indent=2)
        except Exception as e:
            print(f"[Engagement Bot Warning] Could not save replied IDs: {e}")

    def is_configured(self) -> bool:
        return bool(self.page_token and self.fb_page_id)

    def generate_smart_reply(self, comment_text: str, user_name: str = "there", platform: str = "Instagram") -> str:
        """Uses Gemini to generate an authentic, warm, human B2B agency reply answering the user specifically and sharing our site & email."""
        website = BRAND.get("website", "https://knownbydigital.com").strip()
        email = BRAND.get("email", "hello@knownbydigital.com").strip()
        brand_name = BRAND.get("name", "Known By Digital")

        prompt = f"""
You are a warm, genuine, and knowledgeable team member at '{brand_name}' replying to a user's comment on {platform}.
User name: "{user_name}"
User's comment: "{comment_text}"

Company details:
- Website: {website}
- Direct Email: {email}
- Core Expertise: AI Automation, Revenue Systems, High-Converting Digital Infrastructure

CRITICAL INSTRUCTIONS FOR A NATURAL HUMAN REPLY:
1. Speak warmly, respectfully, and authentically like an actual human team member (NOT like a robotic AI, marketing bot, or canned template).
2. Directly answer or address what the user specifically asked or said in their comment. Validate their point or question with genuine insight.
3. Naturally guide them to explore our website ({website}) or reach out directly to our team via email ({email}) if they'd like a custom consultation, demo, or audit.
4. Keep the response concise, punchy, and pleasant (2 to 3 sentences max).
5. Use at most 1 tasteful emoji (e.g., 🚀, 🤝, or ✨).
6. Return ONLY the final reply text string. Do not include quotes, markdown labels, or meta commentary.
"""
        try:
            reply = call_gemini(prompt, response_mime_type="text/plain").strip().strip('"').strip("'")
            if reply and len(reply) > 10:
                return reply
        except Exception as e:
            print(f"[Engagement Bot AI Warning] Gemini reply generation fallback: {e}")

        # Natural human fallback
        if platform == "Instagram":
            return f"Hi @{user_name}! Great question—we'd love to help you scale that. Feel free to explore our solutions at {website} or drop our team a line at {email} 🚀"
        else:
            return f"Hi {user_name}! We'd be happy to help you implement this. Check out our models at {website} or email us directly at {email} 🤝"

    def _reply_to_instagram(self) -> int:
        """Polls recent Instagram media for unreplied comments."""
        if not (self.page_token and self.ig_account_id):
            return 0

        replies = 0
        try:
            media_url = f"{GRAPH_URL}/{self.ig_account_id}/media?fields=id,caption,permalink&limit=5&access_token={self.page_token}"
            media_resp = requests.get(media_url, timeout=30).json()
            media_list = media_resp.get("data", [])
        except Exception as e:
            print(f"[Engagement Bot IG Error] Could not fetch media: {e}")
            return 0

        for media in media_list:
            media_id = media["id"]
            comments_url = f"{GRAPH_URL}/{media_id}/comments?fields=id,text,username,timestamp&limit=10&access_token={self.page_token}"
            try:
                comments_resp = requests.get(comments_url, timeout=30).json()
                comments = comments_resp.get("data", [])
            except Exception:
                continue

            for comment in comments:
                cid = comment["id"]
                if cid in self.replied_comment_ids:
                    continue

                author = comment.get("username", "friend")
                if str(author).lower() in ["knownbydigital", "knownbydigital_"]:
                    continue

                text = comment.get("text", "")
                reply_text = self.generate_smart_reply(text, author, platform="Instagram")

                # Anti-ban human jitter delay
                delay = random.randint(8, 15)
                time.sleep(delay)

                try:
                    reply_endpoint = f"{GRAPH_URL}/{cid}/replies"
                    post_res = requests.post(
                        reply_endpoint,
                        data={"message": reply_text, "access_token": self.page_token},
                        timeout=30
                    ).json()
                    if "id" in post_res:
                        print(f"[Engagement Bot - IG] Replied to @{author}: '{reply_text}'")
                        self.replied_comment_ids.add(cid)
                        self._save_replied_ids()
                        replies += 1

                        # Telegram instant alert
                        try:
                            send_telegram_alert(
                                title="💬 Auto-Replied to Instagram Comment",
                                message=f"<b>User:</b> @{author}\n<b>Comment:</b> {text}\n\n<b>AI Reply:</b> {reply_text}",
                                links={"Post": media.get("permalink", "https://instagram.com/knownbydigital")}
                            )
                        except Exception:
                            pass
                except Exception as e:
                    print(f"[Engagement Bot - IG Error] Reply failed for {cid}: {e}")

                if replies >= 10:
                    break
        return replies

    def _reply_to_facebook(self) -> int:
        """Polls recent Facebook Page posts for unreplied comments."""
        if not (self.page_token and self.fb_page_id):
            return 0

        replies = 0
        try:
            feed_url = f"{GRAPH_URL}/{self.fb_page_id}/feed?fields=id,message&limit=5&access_token={self.page_token}"
            feed_resp = requests.get(feed_url, timeout=30).json()
            posts = feed_resp.get("data", [])
        except Exception as e:
            print(f"[Engagement Bot FB Error] Could not fetch feed: {e}")
            return 0

        for post in posts:
            post_id = post["id"]
            comments_url = f"{GRAPH_URL}/{post_id}/comments?fields=id,message,from&limit=10&access_token={self.page_token}"
            try:
                comments_resp = requests.get(comments_url, timeout=30).json()
                comments = comments_resp.get("data", [])
            except Exception:
                continue

            for comment in comments:
                cid = comment["id"]
                if cid in self.replied_comment_ids:
                    continue

                from_info = comment.get("from", {})
                from_id = str(from_info.get("id", "")).strip()
                author = from_info.get("name", "there")

                if from_id == self.fb_page_id or str(author).lower() in ["known by digital", "knownbydigital"]:
                    continue

                text = comment.get("message", "")
                reply_text = self.generate_smart_reply(text, author, platform="Facebook")

                delay = random.randint(8, 15)
                time.sleep(delay)

                try:
                    reply_endpoint = f"{GRAPH_URL}/{cid}/comments"
                    post_res = requests.post(
                        reply_endpoint,
                        data={"message": reply_text, "access_token": self.page_token},
                        timeout=30
                    ).json()
                    if "id" in post_res:
                        print(f"[Engagement Bot - FB] Replied to {author}: '{reply_text}'")
                        self.replied_comment_ids.add(cid)
                        self._save_replied_ids()
                        replies += 1

                        # Telegram instant alert
                        try:
                            send_telegram_alert(
                                title="💬 Auto-Replied to Facebook Comment",
                                message=f"<b>User:</b> {author}\n<b>Comment:</b> {text}\n\n<b>AI Reply:</b> {reply_text}",
                                links={"Facebook Page": "https://facebook.com/1709963579119224"}
                            )
                        except Exception:
                            pass
                except Exception as e:
                    print(f"[Engagement Bot - FB Error] Reply failed for {cid}: {e}")

                if replies >= 10:
                    break
        return replies

    def _reply_to_threads(self) -> int:
        """Polls recent Threads posts for unreplied comments/replies."""
        if not (self.threads_token and self.threads_user_id):
            return 0

        replies = 0
        try:
            threads_url = f"{THREADS_URL}/{self.threads_user_id}/threads?fields=id,text&limit=5&access_token={self.threads_token}"
            threads_resp = requests.get(threads_url, timeout=30).json()
            thread_list = threads_resp.get("data", [])
        except Exception as e:
            print(f"[Engagement Bot Threads Error] Could not fetch threads: {e}")
            return 0

        for item in thread_list:
            thread_id = item["id"]
            conv_url = f"{THREADS_URL}/{thread_id}/conversation?fields=id,text,username,timestamp&limit=10&access_token={self.threads_token}"
            try:
                conv_resp = requests.get(conv_url, timeout=30).json()
                replies_data = conv_resp.get("data", [])
            except Exception:
                continue

            for reply_item in replies_data:
                rid = reply_item["id"]
                if rid in self.replied_comment_ids:
                    continue
                author = reply_item.get("username", "")
                if str(author).lower() in ["knownbydigital", "knownbydigital_"]:
                    continue

                text = reply_item.get("text", "")
                reply_text = self.generate_smart_reply(text, author, platform="Threads")

                delay = random.randint(8, 15)
                time.sleep(delay)

                try:
                    c_url = f"{THREADS_URL}/{self.threads_user_id}/threads"
                    c_payload = {
                        "media_type": "TEXT",
                        "text": reply_text,
                        "reply_to_id": rid,
                        "access_token": self.threads_token
                    }
                    c_res = requests.post(c_url, data=c_payload, timeout=30).json()
                    creation_id = c_res.get("id")
                    if creation_id:
                        time.sleep(3)
                        pub_url = f"{THREADS_URL}/{self.threads_user_id}/threads_publish"
                        p_res = requests.post(pub_url, data={"creation_id": creation_id, "access_token": self.threads_token}, timeout=30).json()
                        if "id" in p_res:
                            print(f"[Engagement Bot - Threads] Replied to @{author}: '{reply_text}'")
                            self.replied_comment_ids.add(rid)
                            self._save_replied_ids()
                            replies += 1

                            # Telegram instant alert
                            try:
                                send_telegram_alert(
                                    title="💬 Auto-Replied to Threads Reply",
                                    message=f"<b>User:</b> @{author}\n<b>Comment:</b> {text}\n\n<b>AI Reply:</b> {reply_text}",
                                    links={"Threads": "https://www.threads.com/@knownbydigital"}
                                )
                            except Exception:
                                pass
                except Exception as e:
                    print(f"[Engagement Bot - Threads Error] Reply failed for {rid}: {e}")

                if replies >= 10:
                    break
        return replies

    def check_and_reply_comments(self) -> int:
        """Runs the engagement cycle across Instagram, Facebook Page, and Threads."""
        if not self.is_configured():
            print(f"[Engagement Bot - Simulation] Checked for new comments across channels.")
            return 0

        ig_count = self._reply_to_instagram()
        fb_count = self._reply_to_facebook()
        thr_count = self._reply_to_threads()

        total = ig_count + fb_count + thr_count
        return total

if __name__ == "__main__":
    bot = EngagementBot()
    print(f"Checking active comments across Instagram, Facebook Page, and Threads...")
    count = bot.check_and_reply_comments()
    print(f"Engagement check complete. Replied to {count} new comments.")
