import os
import sys
import time
import json
import schedule
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

from cleaner import purge_old_media
from engagement_bot import EngagementBot
from content_engine import generate_daily_social_pack, assemble_seo_caption
from story_generator import generate_pro_story_image
from media_generator import generate_single_post_image, generate_carousel_slides
from reel_generator import generate_faceless_reel
from meta_publisher import MetaPublisher, upload_media_to_public_url
from html_renderer import get_current_day_theme
from notifier import send_telegram_alert
from config import MEDIA_DIR

BASE_DIR = Path(__file__).resolve().parent
CACHED_PACK_FILE = BASE_DIR / "daily_cached_pack.json"

bot = EngagementBot()
publisher = MetaPublisher()

def get_or_create_daily_pack() -> dict:
    today_str = datetime.now().strftime("%Y-%m-%d")
    if CACHED_PACK_FILE.exists():
        try:
            with open(CACHED_PACK_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("date") == today_str and "pack" in data:
                    return data["pack"]
        except Exception:
            pass

    print(f"\n[Scheduler] Generating fresh daily strategic content pack for {today_str}...")
    pack = generate_daily_social_pack()
    with open(CACHED_PACK_FILE, "w", encoding="utf-8") as f:
        json.dump({"date": today_str, "pack": pack}, f, indent=2, ensure_ascii=False)
    return pack

def job_post_reel():
    print(f"\n[Scheduler] 🎬 EXECUTING SCHEDULED REEL (18:30 BST / 08:30 AM EST)")
    try:
        pack = get_or_create_daily_pack()
        theme = get_current_day_theme()
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        reel_video, reel_cover = generate_faceless_reel(pack["reel"], output_filename=f"sched_reel_{date_str}.mp4", theme=theme)
        caption = assemble_seo_caption(pack["reel"])
        
        # 1. Instagram Reel
        res_ig = publisher.publish_instagram_reel(reel_video, caption, cover_path_or_url=reel_cover)
        print(f"[Scheduler] Instagram Reel: {res_ig.get('permalink', res_ig)}")

        # 2. Facebook Reel / Video
        try:
            hook = pack["reel"].get("hook_3s", "Known By Digital Reel")
            res_fb = publisher.publish_facebook_video(reel_video, caption, title=hook)
            print(f"[Scheduler] Facebook Video: {res_fb.get('id', res_fb)}")
        except Exception as fb_err:
            print(f"[Scheduler Note] Facebook Reel cross-post: {fb_err}")

        # 3. Threads Reel Card
        res_threads = {}
        try:
            threads_text = pack["reel"].get("hook_3s", "Known By Digital Reel") + "\n\n" + caption[:400]
            res_threads = publisher.publish_threads_post(threads_text, image_url=reel_cover)
            print(f"[Scheduler] Threads Reel Card: {res_threads.get('permalink', res_threads.get('id', res_threads))}")
        except Exception as thr_err:
            print(f"[Scheduler Note] Threads Reel: {thr_err}")

        # Send Telegram Instant Alert
        links = {}
        if res_ig.get("permalink"):
            links["Instagram Reel"] = res_ig["permalink"]
        if res_fb.get("id"):
            links["Facebook Video"] = f"https://www.facebook.com/{publisher.page_id}/posts/{res_fb['id']}"
        if res_threads.get("permalink"):
            links["Threads"] = res_threads["permalink"]

        send_telegram_alert(
            title="🎬 18:30 BST Reel Published Live!",
            message=f"<b>Theme:</b> {theme.capitalize()}\n<b>Hook:</b> {pack['reel'].get('hook_3s', '')}",
            links=links
        )

    except Exception as e:
        print(f"[Scheduler Error] Reel publishing failed: {e}")
        send_telegram_alert(
            title="Reel Publishing Failed",
            message=f"Error during 18:30 BST Reel execution:\n<code>{e}</code>",
            is_error=True
        )
        raise e

def job_post_story():
    print(f"\n[Scheduler] 📱 EXECUTING SCHEDULED STORY (21:30 BST / 11:30 AM EST)")
    try:
        pack = get_or_create_daily_pack()
        theme = get_current_day_theme()
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        story_img = generate_pro_story_image(pack.get("story", {}), output_filename=f"sched_story_{date_str}.jpg", theme=theme)
        
        # Instagram Story via public URL
        story_url = upload_media_to_public_url(story_img)
        res = publisher.publish_instagram_story(story_url)
        print(f"[Scheduler] Story published successfully. ID: {res.get('story_id')}")

        send_telegram_alert(
            title="📱 21:30 BST Interactive Story Published!",
            message=f"<b>Theme:</b> {theme.capitalize()}\n<b>Question:</b> {pack.get('story', {}).get('poll_question', '')}",
            links={"Instagram Stories": "https://www.instagram.com/stories/knownbydigital/"},
            photo_url=story_url
        )
    except Exception as e:
        print(f"[Scheduler Error] Story publishing failed: {e}")
        send_telegram_alert(
            title="Story Publishing Failed",
            message=f"Error during 21:30 BST Story execution:\n<code>{e}</code>",
            is_error=True
        )
        raise e

def job_post_carousel():
    print(f"\n[Scheduler] 📑 EXECUTING SCHEDULED CAROUSEL (00:30 BST / 02:30 PM EST)")
    try:
        pack = get_or_create_daily_pack()
        theme = get_current_day_theme()
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        carousel_slides = generate_carousel_slides(pack["carousel"], prefix=f"sched_carousel_{date_str}", theme=theme)
        caption = assemble_seo_caption(pack["carousel"])
        
        # Convert slides to public URLs
        carousel_urls = [upload_media_to_public_url(p) for p in carousel_slides]

        # 1. Instagram Carousel
        res_ig = publisher.publish_instagram_carousel(carousel_urls, caption)
        print(f"[Scheduler] Instagram Carousel: {res_ig.get('permalink', res_ig)}")

        # 2. Facebook Multi-Photo Carousel Album Post (all slides)
        try:
            fb_caption = f"📑 {pack['carousel'].get('topic', 'Strategy Guide')}\n\n{caption}"
            res_fb = publisher.publish_facebook_carousel(carousel_slides, fb_caption)
            print(f"[Scheduler] Facebook Carousel Album: {res_fb.get('id', res_fb)}")
        except Exception as fb_err:
            print(f"[Scheduler Note] Facebook Carousel: {fb_err}")

        # 3. Threads Carousel Preview
        res_threads = {}
        try:
            thr_caption = f"📑 {pack['carousel'].get('topic', 'Strategy Guide')}\n\n{caption[:400]}"
            cover_url = carousel_urls[0] if carousel_urls else None
            res_threads = publisher.publish_threads_post(thr_caption, image_url=cover_url)
            print(f"[Scheduler] Threads Carousel Preview: {res_threads.get('permalink', res_threads.get('id', res_threads))}")
        except Exception as thr_err:
            print(f"[Scheduler Note] Threads Carousel: {thr_err}")

        # Send Telegram Instant Alert
        links = {}
        if res_ig.get("permalink"):
            links["Instagram Carousel"] = res_ig["permalink"]
        if res_fb.get("id"):
            links["Facebook Post"] = f"https://www.facebook.com/{publisher.page_id}/posts/{res_fb['id']}"
        if res_threads.get("permalink"):
            links["Threads"] = res_threads["permalink"]

        send_telegram_alert(
            title="📑 00:30 BST Strategy Carousel Published!",
            message=f"<b>Theme:</b> {theme.capitalize()}\n<b>Topic:</b> {pack['carousel'].get('topic', '')}",
            links=links,
            photo_url=carousel_urls[0] if carousel_urls else None
        )

    except Exception as e:
        print(f"[Scheduler Error] Carousel publishing failed: {e}")
        send_telegram_alert(
            title="Carousel Publishing Failed",
            message=f"Error during 00:30 BST Carousel execution:\n<code>{e}</code>",
            is_error=True
        )
        raise e

def job_post_single_post():
    print(f"\n[Scheduler] 🖼️ EXECUTING SCHEDULED SINGLE POST (14:00 BST / 09:00 AM UK)")
    try:
        pack = get_or_create_daily_pack()
        theme = get_current_day_theme()
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        post_img = generate_single_post_image(pack["single_post"], output_filename=f"sched_post_{date_str}.png", theme=theme)
        caption = assemble_seo_caption(pack["single_post"])
        
        # 1. Publish to Facebook Page FIRST (direct file upload to Meta server)
        fb_img_url = None
        res_fb = {}
        try:
            res_fb = publisher.publish_facebook_post(caption, image_path=post_img)
            print(f"[Scheduler] Facebook Post: {res_fb.get('id', res_fb)}")
            fb_photo_id = res_fb.get("id")
            if fb_photo_id:
                try:
                    import requests
                    from meta_publisher import GRAPH_URL
                    img_data = requests.get(f"{GRAPH_URL}/{fb_photo_id}?fields=images&access_token={publisher.page_token}", timeout=15).json()
                    images = img_data.get("images", [])
                    if images:
                        fb_img_url = images[0].get("source")
                except Exception:
                    pass
        except Exception as fb_err:
            print(f"[Scheduler Note] Facebook Post: {fb_err}")

        # 2. Upload to public CDN if FB CDN is unavailable
        img_pub_url = fb_img_url or upload_media_to_public_url(post_img)

        # 3. Instagram Photo (using internal Meta CDN or fallback)
        res_ig = publisher.publish_instagram_photo(img_pub_url, caption)
        print(f"[Scheduler] Instagram Photo: {res_ig.get('permalink', res_ig)}")

        # 4. Threads Post (via Meta CDN or public URL)
        res_threads = {}
        try:
            threads_text = pack["single_post"].get("threads_version") or caption[:490]
            res_threads = publisher.publish_threads_post(threads_text, image_url=img_pub_url)
            print(f"[Scheduler] Threads Post: {res_threads.get('id', res_threads)}")
        except Exception as thr_err:
            print(f"[Scheduler Note] Threads Post: {thr_err}")

        # Send Telegram Instant Alert
        links = {}
        if res_ig.get("permalink"):
            links["Instagram"] = res_ig["permalink"]
        if res_fb.get("id"):
            links["Facebook"] = f"https://www.facebook.com/{publisher.page_id}/posts/{res_fb['id']}"
        if res_threads.get("permalink"):
            links["Threads"] = res_threads["permalink"]

        send_telegram_alert(
            title="🖼️ 14:00 BST Single Post Published!",
            message=f"<b>Theme:</b> {theme.capitalize()}\n<b>Headline:</b> {pack['single_post'].get('headline', '')}",
            links=links,
            photo_url=img_pub_url
        )

    except Exception as e:
        print(f"[Scheduler Error] Single post publishing failed: {e}")
        send_telegram_alert(
            title="Single Post Publishing Failed",
            message=f"Error during 14:00 BST Single Post execution:\n<code>{e}</code>",
            is_error=True
        )
        raise e

def job_check_comments():
    try:
        replies = bot.check_and_reply_comments()
        if replies > 0:
            print(f"[Scheduler] Engagement Bot posted {replies} smart replies.")
    except Exception as e:
        print(f"[Scheduler Warning] Engagement check error: {e}")

def job_clean_storage():
    print(f"\n[Scheduler] 🧹 RUNNING DAILY STORAGE PURGE (48h Retention Policy)")
    try:
        purge_old_media()
    except Exception as e:
        print(f"[Scheduler Warning] Cleaner error: {e}")

def job_refresh_tokens():
    print(f"\n[Scheduler] 🔄 REFRESHING THREADS ACCESS TOKEN (Auto-Extend 60 Days)")
    try:
        res = publisher.refresh_threads_token()
        print(f"[Scheduler] Threads token refresh result: {res}")
    except Exception as e:
        print(f"[Scheduler Warning] Token refresh error: {e}")

def start_scheduler():
    print("=" * 65)
    print("⚡ KNOWN BY DIGITAL AUTONOMOUS MULTI-CHANNEL SOCIAL SCHEDULER")
    print(f"⏰ Active Local Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} BST")
    print("=" * 65)
    print("📅 Fully Autonomous Daily Slots (Instagram, Facebook & Threads):")
    print("   1. 🖼️ 14:00 BST (09:00 AM UK / 04:00 AM EST) -> Single Post (IG + FB + Threads)")
    print("   2. 🎬 18:30 BST (01:30 PM UK / 08:30 AM EST) -> Reel (7-15s + Cover) (IG + FB + Threads)")
    print("   3. 📱 21:30 BST (04:30 PM UK / 11:30 AM EST) -> Interactive Story (Instagram)")
    print("   4. 📑 00:30 BST (07:30 PM UK / 02:30 PM EST) -> Carousel (5 Slides) (IG + FB + Threads)")
    print("   5. 💬 Every 20 Minutes                       -> Engagement Bot (Smart Comment Reply)")
    print("   6. 🧹 Daily at 03:00 BST                     -> Storage Auto-Purge (48h Retention)")
    print("   7. 🔄 Weekly on Sunday 04:00 BST             -> Threads Token Auto-Refresh (Never Expires)")
    print("=" * 65)

    # Schedule the 4 peak-hour posts
    schedule.every().day.at("14:00").do(job_post_single_post)
    schedule.every().day.at("18:30").do(job_post_reel)
    schedule.every().day.at("21:30").do(job_post_story)
    schedule.every().day.at("00:30").do(job_post_carousel)

    # Schedule engagement comment checks every 20 minutes
    schedule.every(20).minutes.do(job_check_comments)

    # Schedule daily storage purge at 03:00 AM
    schedule.every().day.at("03:00").do(job_clean_storage)

    # Schedule weekly Threads token refresh
    schedule.every().sunday.at("04:00").do(job_refresh_tokens)

    # Initial engagement check on startup
    job_check_comments()

    print("\n🟢 Multi-channel daemon is active. Running autonomously in background...")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check-comments":
        job_check_comments()
    elif len(sys.argv) > 1 and sys.argv[1] == "--clean":
        job_clean_storage()
    else:
        start_scheduler()
