import time
import sys
import schedule
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from run_daily_pipeline import run_pipeline
from engagement_bot import EngagementBot
from cleaner import purge_old_media

def job_daily():
    print(f"\n[Scheduler] Triggering Daily Social Media Pipeline at {datetime.now()}...")
    try:
        run_pipeline()
    except Exception as e:
        print(f"[Scheduler Error] Daily pipeline failed: {e}")

def job_engagement():
    try:
        bot = EngagementBot()
        bot.check_and_reply_comments()
    except Exception as e:
        print(f"[Scheduler Error] Engagement check failed: {e}")

def job_cleanup():
    purge_old_media()

def start_scheduler():
    print("=" * 60)
    print("🤖 KNOWN BY DIGITAL 24/7 BACKGROUND DAEMON STARTED")
    print("• Daily Post Schedule: Every day at 19:00 BST (US/UK Peak Time)")
    print("• Comment Auto-Reply: Every 15 minutes (with anti-ban human delay)")
    print("• Storage Auto-Cleaner: Enforces strict 48-hour retention")
    print("=" * 60)

    # 1. Schedule daily post at 19:00 (7:00 PM BST / 9:00 AM EST)
    schedule.every().day.at("19:00").do(job_daily)

    # 2. Schedule comment check every 15 minutes
    schedule.every(15).minutes.do(job_engagement)

    # 3. Storage cleaner check every 6 hours
    schedule.every(6).hours.do(job_cleanup)

    # Run initial checks on start
    job_cleanup()

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    start_scheduler()
