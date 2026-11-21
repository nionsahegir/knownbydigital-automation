import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from content_engine import generate_daily_social_pack, assemble_seo_caption
from media_generator import generate_single_post_image, generate_carousel_slides
from reel_generator import generate_faceless_reel
from story_generator import generate_pro_story_image
from meta_publisher import MetaPublisher
from html_renderer import get_current_day_theme
from config import MEDIA_DIR

def run_omnichannel_generation_and_publishing():
    theme = "dark" # Dark provides maximum contrast and sleek agency aesthetic
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("=" * 60)
    print("🚀 PUBLISHING 4 ASSETS: STORY, SINGLE POST, CAROUSEL, REEL")
    print("=" * 60)

    # 1. Generate Fresh AI Pack
    print("\n[Step 1/5] Generating fresh strategic social pack via Google Gemini...")
    pack = generate_daily_social_pack()
    print(f"   ✓ Reel Hook: {pack['reel']['hook_3s']}")
    print(f"   ✓ Post Headline: {pack['single_post']['headline']}")
    print(f"   ✓ Carousel Topic: {pack['carousel']['topic']}")

    publisher = MetaPublisher()
    published_links = {}

    # 2. STORY (Asset 1/4)
    print("\n[Step 2/5] Creating & Publishing Instagram Story...")
    story_img = generate_pro_story_image(output_filename=f"story_{date_str}.jpg", theme=theme)
    story_res = publisher.publish_instagram_story(story_img)
    published_links["story"] = story_res
    print(f"   🎉 Story Result: {story_res}")

    # Brief delay between uploads
    time.sleep(4)

    # 3. SINGLE POST (Asset 2/4)
    print("\n[Step 3/5] Creating & Publishing Single Post (Micro-Blog Caption)...")
    post_img = generate_single_post_image(pack["single_post"], output_filename=f"post_{date_str}.png", theme=theme)
    post_caption = assemble_seo_caption(pack["single_post"])
    post_res = publisher.publish_instagram_photo(post_img, post_caption)
    published_links["single_post"] = post_res
    print(f"   🎉 Single Post URL: {post_res.get('permalink')}")

    # Brief delay between uploads
    time.sleep(4)

    # 4. CAROUSEL (Asset 3/4)
    print("\n[Step 4/5] Creating & Publishing 5-Slide Infographic Carousel...")
    carousel_slides = generate_carousel_slides(pack["carousel"], prefix=f"carousel_{date_str}", theme=theme)
    carousel_caption = assemble_seo_caption(pack["carousel"])
    carousel_res = publisher.publish_instagram_carousel(carousel_slides, carousel_caption)
    published_links["carousel"] = carousel_res
    print(f"   🎉 Carousel URL: {carousel_res.get('permalink')}")

    # Brief delay between uploads
    time.sleep(4)

    # 5. REEL (Asset 4/4)
    print("\n[Step 5/5] Creating & Publishing 7-15s Micro-Reel with Animated Mascot & Dedicated Cover...")
    reel_video, reel_cover = generate_faceless_reel(pack["reel"], output_filename=f"reel_{date_str}.mp4", theme=theme)
    reel_caption = assemble_seo_caption(pack["reel"])
    reel_res = publisher.publish_instagram_reel(reel_video, reel_caption, cover_path_or_url=reel_cover)
    published_links["reel"] = reel_res
    print(f"   🎉 Reel URL: {reel_res.get('permalink')}")

    print("\n" + "=" * 60)
    print("✅ ALL 4 SOCIAL ASSETS PUBLISHED TO INSTAGRAM!")
    print(json.dumps(published_links, indent=2))
    print("=" * 60)
    return published_links

if __name__ == "__main__":
    run_omnichannel_generation_and_publishing()
