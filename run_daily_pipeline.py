import json
import time
import sys
from datetime import datetime

# Ensure Windows terminal outputs UTF-8 cleanly
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from cleaner import purge_old_media
from content_engine import generate_daily_social_pack, assemble_seo_caption
from media_generator import generate_single_post_image, generate_carousel_slides
from reel_generator import generate_faceless_reel
from story_generator import generate_pro_story_image
from meta_publisher import MetaPublisher
from html_renderer import get_current_day_theme
from engagement_bot import EngagementBot
from config import MEDIA_DIR

def run_pipeline(dry_run: bool = False, theme: str = None):
    if not theme:
        theme = get_current_day_theme()

    print("=" * 60)
    print(f"🚀 KNOWN BY DIGITAL SOCIAL AUTOMATION PIPELINE")
    print(f"⏰ Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎨 Today's Active Brand Theme: {theme.upper()} (3-Day Feed Cycle)")
    print("=" * 60)

    # STEP 1: Auto-Cleanup (Keeps storage clean, deletes files > 48h)
    print("\n[Step 1/5] Running Storage Auto-Cleaner (48h Retention Policy)...")
    purge_old_media()

    # STEP 2: Content Generation via Google Gemini API
    print("\n[Step 2/5] Generating Daily Social Media Pack via Google Gemini...")
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    pack = generate_daily_social_pack()

    print(f"   ✓ Reel Topic: {pack['reel']['topic']}")
    print(f"   ✓ Post Headline: {pack['single_post']['headline']}")
    print(f"   ✓ Carousel Topic: {pack['carousel']['topic']}")

    # STEP 3: Media Asset Generation (Branded Graphics, Story & Faceless Reel in Active Theme)
    print(f"\n[Step 3/5] Generating Visual Assets, Story & Faceless Reel in [{theme.upper()}] Theme...")
    story_img_path = generate_pro_story_image(pack.get("story", {}), output_filename=f"story_{date_str}.jpg", theme=theme)
    post_img_path = generate_single_post_image(pack["single_post"], output_filename=f"post_{date_str}.png", theme=theme)
    carousel_slide_paths = generate_carousel_slides(pack["carousel"], prefix=f"carousel_{date_str}", theme=theme)
    reel_video_path, reel_cover_path = generate_faceless_reel(pack["reel"], output_filename=f"reel_{date_str}.mp4", theme=theme)
    
    # Save reel script to text
    reel_script_file = MEDIA_DIR / f"reel_script_{date_str}.txt"
    with open(reel_script_file, "w", encoding="utf-8") as rf:
        rf.write(f"HOOK: {pack['reel']['hook_3s']}\n\n")
        rf.write(f"VOICEOVER SCRIPT:\n{pack['reel']['voiceover_script']}\n\n")
        rf.write(f"VISUAL CUES:\n{pack['reel']['b_roll_visuals']}\n\n")
        rf.write(f"CAPTION:\n{assemble_seo_caption(pack['reel'])}\n")

    media_assets = {
        "story_image": story_img_path,
        "single_post_image": post_img_path,
        "carousel_slides": carousel_slide_paths,
        "reel_video": reel_video_path,
        "reel_cover": reel_cover_path,
        "reel_script": str(reel_script_file)
    }
    print(f"   ✓ Story card: {story_img_path}")
    print(f"   ✓ Single post card: {post_img_path}")
    print(f"   ✓ Carousel slides: {len(carousel_slide_paths)} slides created")
    print(f"   ✓ Faceless Reel video: {reel_video_path}")
    print(f"   ✓ Reel Cover thumbnail: {reel_cover_path}")
    print(f"   ✓ Reel script: {reel_script_file}")

    # Save summary metadata
    summary_path = MEDIA_DIR / f"summary_{date_str}.json"
    with open(summary_path, "w", encoding="utf-8") as sf:
        json.dump({"pack": pack, "media": media_assets}, sf, indent=2)

    # STEP 4: Omnichannel Dispatch (Instagram, Facebook, Threads)
    print("\n[Step 4/5] Dispatching to Meta Omnichannel (IG, FB, Threads)...")
    publisher = MetaPublisher()
    dispatch_results = publisher.broadcast_daily_pack(pack, media_assets)
    print("   ✓ Dispatch Results:", dispatch_results)

    # STEP 5: Safe Engagement Check
    print("\n[Step 5/5] Checking Engagement & Comments...")
    bot = EngagementBot()
    bot.check_and_reply_comments()

    print("\n" + "=" * 60)
    print("✅ Daily Social Automation Pipeline completed successfully!")
    print("=" * 60)
    return summary_path

if __name__ == "__main__":
    run_pipeline()
