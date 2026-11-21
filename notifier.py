import os
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

def send_telegram_alert(
    title: str,
    message: str = "",
    links: dict = None,
    photo_url: str = None,
    is_error: bool = False
) -> bool:
    """
    Sends an instant push notification to Telegram.
    Zero external dependencies, 100% reliable from GitHub Actions & local runners.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN") or TELEGRAM_BOT_TOKEN
    chat_id = os.getenv("TELEGRAM_CHAT_ID") or TELEGRAM_CHAT_ID

    if not (token and chat_id):
        print("[Notifier Note] Telegram token or chat_id not set. Skipping push alert.")
        return False

    status_icon = "🚨 <b>ALERT: System Error</b>" if is_error else "🚀 <b>Known By Digital — Live Update</b>"
    
    lines = [
        status_icon,
        f"<b>{title}</b>",
        ""
    ]
    
    if message:
        lines.append(message)
        lines.append("")

    if links:
        lines.append("🔗 <b>Live Links:</b>")
        for platform, url in links.items():
            if url and str(url).startswith("http"):
                lines.append(f"• <b>{platform}:</b> <a href=\"{url}\">Open Link</a>")
            elif url:
                lines.append(f"• <b>{platform}:</b> {url}")

    text_body = "\n".join(lines)

    try:
        if photo_url and str(photo_url).startswith("http"):
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            payload = {
                "chat_id": chat_id,
                "photo": photo_url,
                "caption": text_body[:1024],
                "parse_mode": "HTML"
            }
        else:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text_body[:4096],
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }

        resp = requests.post(url, data=payload, timeout=20).json()
        if resp.get("ok"):
            print("[Notifier] Telegram push alert delivered successfully.")
            return True
        else:
            print(f"[Notifier Warning] Telegram API returned: {resp}")
            return False
    except Exception as e:
        print(f"[Notifier Error] Could not send Telegram alert: {e}")
        return False

if __name__ == "__main__":
    print("Testing notifier bridge...")
    res = send_telegram_alert(
        title="Test Notification",
        message="This is a test notification from Known By Digital Social Automation.",
        links={"Instagram": "https://instagram.com/knownbydigital"}
    )
    print("Delivered:", res)
