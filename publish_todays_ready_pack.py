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
from story_generator import generate_pro_story_image
from media_generator import generate_single_post_image, generate_carousel_slides
from reel_generator import generate_faceless_reel
from html_renderer import get_current_day_theme
from config import MEDIA_DIR

BASE_DIR = Path(__file__).resolve().parent
CACHED_PACK_FILE = BASE_DIR / "daily_cached_pack.json"

def publish_todays_pack():
    print("=" * 60)
    print("🚀 PUBLISHING TODAY'S PACK TO INSTAGRAM")
    print(f"⏰ Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    with open(CACHED_PACK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    pack = data["pack"]

    publisher = MetaPublisher()
    theme = "dark"
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {}

    # 1. STORY
    print("\n[1/4] Publishing Instagram Story...")
    story_img = generate_pro_story_image(pack.get("story", {}), output_filename=f"today_story_{date_str}.jpg", theme=theme)
    story_res = publisher.publish_instagram_story(story_img)
    results["story"] = story_res
    print(f"   ✓ Story published: ID {story_res.get('story_id')}")

    time.sleep(4)

    # 2. SINGLE POST
    print("\n[2/4] Publishing Single Post...")
    post_img = generate_single_post_image(pack["single_post"], output_filename=f"today_post_{date_str}.png", theme=theme)
    post_caption = assemble_seo_caption(pack["single_post"])
    post_res = publisher.publish_instagram_photo(post_img, post_caption)
    results["single_post"] = post_res
    print(f"   ✓ Single Post published: {post_res.get('permalink')}")

    time.sleep(4)

    # 3. CAROUSEL
    print("\n[3/4] Publishing Carousel (5 Slides)...")
    carousel_slides = generate_carousel_slides(pack["carousel"], prefix=f"today_carousel_{date_str}", theme=theme)
    carousel_caption = assemble_seo_caption(pack["carousel"])
    carousel_res = publisher.publish_instagram_carousel(carousel_slides, carousel_caption)
    results["carousel"] = carousel_res
    print(f"   ✓ Carousel published: {carousel_res.get('permalink')}")

    time.sleep(4)

    # 4. REEL
    print("\n[4/4] Publishing 7-15s Micro-Reel with Custom Cover...")
    reel_video, reel_cover = generate_faceless_reel(pack["reel"], output_filename=f"today_reel_{date_str}.mp4", theme=theme)
    reel_caption = assemble_seo_caption(pack["reel"])
    reel_res = publisher.publish_instagram_reel(reel_video, reel_caption, cover_path_or_url=reel_cover)
    results["reel"] = reel_res
    print(f"   ✓ Reel published: {reel_res.get('permalink')}")

    print("\n" + "=" * 60)
    print("🎉 ALL 4 ASSETS PUBLISHED TO INSTAGRAM!")
    print(json.dumps(results, indent=2))
    print("=" * 60)
    return results

if __name__ == "__main__":
    publish_todays_pack()
