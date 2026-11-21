import os
from pathlib import Path
from config import BRAND, MEDIA_DIR

# Import the new High-End HTML/CSS Agency Renderer
try:
    from html_renderer import generate_pro_carousel_slides, generate_pro_single_post_image
    HAS_PRO_RENDERER = True
except ImportError:
    HAS_PRO_RENDERER = False

def generate_single_post_image(post_data: dict, output_filename: str = "single_post.png", theme: str = None) -> str:
    """Uses the agency-grade HTML5/CSS3 renderer for Figma-quality graphics."""
    if HAS_PRO_RENDERER:
        try:
            return generate_pro_single_post_image(post_data, output_filename, theme=theme)
        except Exception as e:
            print(f"[Renderer Notice] Pro renderer fallback triggered: {e}")
            
    # Fallback to Pillow
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (1080, 1080), BRAND["primary_dark"])
    draw = ImageDraw.Draw(img)
    draw.text((100, 400), post_data.get("image_card_title", "KNOWN BY DIGITAL"), fill=(255, 255, 255))
    out_path = MEDIA_DIR / output_filename
    img.save(out_path)
    return str(out_path)

def generate_carousel_slides(carousel_data: dict, prefix: str = "carousel", theme: str = None) -> list:
    """Uses the agency-grade HTML5/CSS3 renderer for 4:5 carousel slides."""
    if HAS_PRO_RENDERER:
        try:
            return generate_pro_carousel_slides(carousel_data, prefix, theme=theme)
        except Exception as e:
            print(f"[Renderer Notice] Pro carousel fallback triggered: {e}")

    # Fallback
    from PIL import Image
    out_files = []
    for idx in range(len(carousel_data.get("slides", []))):
        img = Image.new("RGB", (1080, 1350), BRAND["primary_dark"])
        p = str(MEDIA_DIR / f"{prefix}_slide_{idx+1}.png")
        img.save(p)
        out_files.append(p)
    return out_files

if __name__ == "__main__":
    print("Testing Pro HTML Agency Renderer...")
    test_carousel = {
        "slides": [
            {
                "type": "cover",
                "headline": "The 2026 Shopify Tech Stack",
                "subheadline": "How top 7-figure brands cut operations by 40% with autonomous AI agents."
            },
            {
                "type": "problem",
                "headline": "Why Traditional CX is Bleeding Cash",
                "points": [
                    "Manual lead response delays cost 60% of buyers",
                    "Support agents spend 80% time on basic repetitive FAQs",
                    "Customer acquisition costs jumped 44% year-over-year"
                ]
            },
            {
                "type": "solution_framework",
                "headline": "The Autonomous Revenue Loop",
                "points": [
                    "Instant intent detection across Meta & Shopify",
                    "AI agent answers, recommends & qualifies in 4 seconds",
                    "Seamless CRM synchronization without human prompts"
                ]
            },
            {
                "type": "cta",
                "headline": "Make Your Brand AI-Ready in 2026",
                "subheadline": "Comment 'SYSTEM' or DM @knownbydigital to claim your custom agency blueprint."
            }
        ]
    }
    slides = generate_carousel_slides(test_carousel, prefix="agency_preview")
    print("Generated Slides:", slides)
