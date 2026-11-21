import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output on all platforms
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

from scheduler_daemon import (
    job_post_single_post,
    job_post_reel,
    job_post_story,
    job_post_carousel,
    job_check_comments,
    job_clean_storage,
    job_refresh_tokens
)

def run_auto_job(schedule_cron: str = None):
    """
    Selects job using either the exact triggering cron expression,
    or generous time windows to accommodate GitHub Actions queue latency (15-60 min).
    """
    if schedule_cron:
        cron_clean = schedule_cron.strip()
        print(f"[RunJob Auto] Resolving via triggering schedule cron: '{cron_clean}'")
        if "0 8" in cron_clean:
            return job_post_single_post()
        elif "30 12" in cron_clean:
            return job_post_reel()
        elif "30 15" in cron_clean:
            return job_post_story()
        elif "30 18" in cron_clean:
            return job_post_carousel()
        elif "0 21" in cron_clean:
            return job_clean_storage()
        elif "0 22" in cron_clean:
            return job_refresh_tokens()

    # Fallback to generous time windows (UTC):
    utc_now = datetime.utcnow()
    h = utc_now.hour
    m = utc_now.minute
    print(f"[RunJob Auto] Current UTC time: {utc_now.strftime('%Y-%m-%d %H:%M:%S UTC')} (Hour: {h}:{m:02d})")

    # Time Windows (accommodates up to 2 hours of runner queue delay):
    # 08:00 - 11:59 UTC (14:00 - 17:59 BST) -> Single Post
    # 12:00 - 14:59 UTC (18:00 - 20:59 BST) -> Reel
    # 15:00 - 17:59 UTC (21:00 - 23:59 BST) -> Story
    # 18:00 - 03:59 UTC (00:00 - 09:59 BST) -> Carousel
    if 8 <= h < 12:
        print("[RunJob Auto] Matched Window: 14:00 BST Slot (Single Post)")
        job_post_single_post()
    elif 12 <= h < 15:
        print("[RunJob Auto] Matched Window: 18:30 BST Slot (Reel)")
        job_post_reel()
    elif 15 <= h < 18:
        print("[RunJob Auto] Matched Window: 21:30 BST Slot (Story)")
        job_post_story()
    elif 18 <= h <= 23 or 0 <= h < 4:
        print("[RunJob Auto] Matched Window: 00:30 BST Slot (Carousel)")
        job_post_carousel()
    else:
        print("[RunJob Auto] Daytime off-slot. Running engagement comment check.")
        job_check_comments()

def main():
    parser = argparse.ArgumentParser(description="Known By Digital Scheduled Job Runner")
    parser.add_argument(
        "--job",
        choices=["single_post", "reel", "story", "carousel", "check_comments", "clean", "refresh_tokens", "auto"],
        default="auto",
        help="Specify which task to run"
    )
    parser.add_argument(
        "--schedule-cron",
        type=str,
        default="",
        help="The GitHub schedule cron expression that triggered the run"
    )
    args = parser.parse_args()

    print(f"🚀 Running job: '{args.job}' at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.job == "single_post":
        job_post_single_post()
    elif args.job == "reel":
        job_post_reel()
    elif args.job == "story":
        job_post_story()
    elif args.job == "carousel":
        job_post_carousel()
    elif args.job == "check_comments":
        job_check_comments()
    elif args.job == "clean":
        job_clean_storage()
    elif args.job == "refresh_tokens":
        job_refresh_tokens()
    elif args.job == "auto":
        run_auto_job(schedule_cron=args.schedule_cron)

if __name__ == "__main__":
    main()
