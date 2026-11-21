import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

from meta_publisher import MetaPublisher
from content_engine import assemble_seo_caption
from reel_generator import generate_faceless_reel

BASE_DIR = Path(__file__).resolve().parent
CACHED_PACK_FILE = BASE_DIR / "daily_cached_pack.json"

def publish_reel():
    print("=" * 60)
    print("🎬 GENERATING & PUBLISHING TODAY'S 7-15s REEL")
    print(f"⏰ Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    with open(CACHED_PACK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    pack = data["pack"]
    reel_data = pack["reel"]

    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_video = f"today_reel_{date_str}.mp4"

    print(f"\n[Step 1] Generating Canva-style motion Reel & custom cover thumbnail...")
    reel_video, reel_cover = generate_faceless_reel(reel_data, output_filename=out_video, theme="dark")
    print(f"   ✓ Video generated: {reel_video}")
    print(f"   ✓ Custom cover generated: {reel_cover}")

    print(f"\n[Step 2] Assembling caption and publishing to Instagram...")
    caption = assemble_seo_caption(reel_data)
    publisher = MetaPublisher()
    res = publisher.publish_instagram_reel(reel_video, caption, cover_path_or_url=reel_cover)

    print("\n" + "=" * 60)
    print(f"🎉 INSTAGRAM REEL PUBLISHED!")
    print(f"Permalink: {res.get('permalink')}")
    print(f"Result details: {json.dumps(res, indent=2)}")
    print("=" * 60)
    return res

if __name__ == "__main__":
    publish_reel()
