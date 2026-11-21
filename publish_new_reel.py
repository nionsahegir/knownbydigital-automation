import os
import sys
import time
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from reel_generator import generate_faceless_reel
from meta_publisher import MetaPublisher
from content_engine import assemble_seo_caption

def publish_micro_reel():
    print("=" * 60)
    print("🎬 GENERATING & PUBLISHING IMPROVED MICRO-REEL (7-15s)")
    print("=" * 60)

    reel_data = {
        "topic": "Autonomous AI Intake for High-Growth Brands",
        "hook_3s": "Stop Chasing Leads Manually",
        "voiceover_script": (
            "Stop losing 70% of inbound sales to slow manual replies. "
            "In 2026, top brands deploy autonomous AI agents that qualify and book in 4 seconds. "
            "Comment SYSTEM to get the blueprint."
        ),
        "cta_trigger_word": "SYSTEM",
        "hashtags": ["#AIAutomation", "#B2BGrowth", "#KnownByDigital"]
    }

    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"micro_reel_{date_str}.mp4"

    print("\n[Step 1/2] Generating Reel video with centered text, animated mascot & dedicated cover...")
    reel_video, reel_cover = generate_faceless_reel(reel_data, output_filename=output_filename, theme="dark")
    print(f"   ✓ Video generated: {reel_video}")
    print(f"   ✓ Cover generated: {reel_cover}")

    print("\n[Step 2/2] Publishing Reel to Instagram with custom cover_url...")
    publisher = MetaPublisher()
    caption = (
        "Stop losing deals to slow follow-up lag.\n\n"
        "Deploy 24/7 autonomous intake that qualifies high-intent buyers in 4 seconds flat.\n\n"
        "Comment SYSTEM below or visit knownbydigital.com to claim the SOP.\n\n"
        "#AIAutomation #B2BGrowth #LeadGeneration #KnownByDigital"
    )
    result = publisher.publish_instagram_reel(reel_video, caption, cover_path_or_url=reel_cover)
    print("\n" + "=" * 60)
    print("🎉 REEL PUBLISH RESULT:", result)
    print("=" * 60)
    return result

if __name__ == "__main__":
    publish_micro_reel()
