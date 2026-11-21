import os
import sys
import base64
from pathlib import Path
from datetime import datetime
from config import BRAND, MEDIA_DIR

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent

THEME_CONFIGS = {
    "dark": {
        "name": "dark",
        "bg_color": "#0A0A0A",
        "bg_gradient": "radial-gradient(circle at 50% 10%, rgba(249, 115, 22, 0.08) 0%, transparent 60%), radial-gradient(circle at 50% 90%, rgba(255, 85, 0, 0.06) 0%, transparent 60%)",
        "text_color": "#FFFFFF",
        "sub_color": "#A3A3A3",
        "accent_color": "#F97316",
        "card_bg": "#121212",
        "card_border": "#262626",
        "row_bg": "#171717",
        "row_border": "#262626",
        "pill_bg": "#171717",
        "pill_border": "#262626",
        "pill_text": "#A3A3A3",
        "btn_bg": "linear-gradient(135deg, #F97316 0%, #EA580C 100%)",
        "btn_color": "#000000",
        "footer_border": "#1F1F1F",
        "logo_file": "kbd_logo_dark_theme.png"
    },
    "light": {
        "name": "light",
        "bg_color": "#FAFAFA",
        "bg_gradient": "radial-gradient(circle at 50% 10%, rgba(249, 115, 22, 0.05) 0%, transparent 60%)",
        "text_color": "#0F172A",
        "sub_color": "#475569",
        "accent_color": "#EA580C",
        "card_bg": "#FFFFFF",
        "card_border": "#E2E8F0",
        "row_bg": "#F8FAFC",
        "row_border": "#E2E8F0",
        "pill_bg": "#F1F5F9",
        "pill_border": "#CBD5E1",
        "pill_text": "#475569",
        "btn_bg": "linear-gradient(135deg, #EA580C 0%, #C2410C 100%)",
        "btn_color": "#FFFFFF",
        "footer_border": "#E2E8F0",
        "logo_file": "kbd_logo_light_theme.png"
    },
    "orange": {
        "name": "orange",
        "bg_color": "#EA580C",
        "bg_gradient": "radial-gradient(circle at 50% 0%, #FB923C 0%, #EA580C 100%)",
        "text_color": "#FFFFFF",
        "sub_color": "rgba(255, 255, 255, 0.92)",
        "accent_color": "#0A0A0A",
        "card_bg": "rgba(0, 0, 0, 0.15)",
        "card_border": "rgba(255, 255, 255, 0.25)",
        "row_bg": "rgba(0, 0, 0, 0.2)",
        "row_border": "rgba(255, 255, 255, 0.25)",
        "pill_bg": "rgba(0, 0, 0, 0.2)",
        "pill_border": "rgba(255, 255, 255, 0.3)",
        "pill_text": "#FFFFFF",
        "btn_bg": "#0A0A0A",
        "btn_color": "#FFFFFF",
        "footer_border": "rgba(255, 255, 255, 0.25)",
        "logo_file": "kbd_logo_white_pure.png"
    }
}

def get_current_day_theme() -> str:
    """Gets today's theme from the persistent 3-day brand rotation manager: dark -> orange -> light."""
    try:
        from theme_manager import get_today_theme
        return get_today_theme()
    except Exception:
        themes = ["dark", "orange", "light"]
        return themes[datetime.now().timetuple().tm_yday % 3]


def get_theme_logo_base64(theme: str) -> str:
    t_cfg = THEME_CONFIGS.get(theme, THEME_CONFIGS["dark"])
    logo_file = BASE_DIR / t_cfg["logo_file"]
    if not logo_file.exists():
        logo_file = BASE_DIR / "kbd_full_logo.png"
    if logo_file.exists():
        with open(logo_file, "rb") as lf:
            return base64.b64encode(lf.read()).decode("utf-8")
    return ""

def get_logo_base64():
    return get_theme_logo_base64("dark")

HTML_TEMPLATE_KBD_CAROUSEL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800;900&family=Inter:wght@400;500;600;700;800&display=swap');
  
  * {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }}

  body {{
    width: 1080px;
    height: 1350px;
    background-color: {bg_color};
    background-image: {bg_gradient};
    color: {text_color};
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 60px 80px;
    overflow: hidden;
    position: relative;
  }}

  /* Top Section: Logo & Counter */
  .top-section {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    z-index: 10;
  }}

  .logo-container {{
    display: flex;
    align-items: center;
    gap: 15px;
  }}

  .logo-img {{
    height: 60px;
    width: auto;
    object-fit: contain;
  }}

  .counter-pill {{
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 2px;
    color: {pill_text};
    background: {pill_bg};
    border: 1px solid {pill_border};
    padding: 10px 22px;
    border-radius: 999px;
  }}

  .counter-pill span {{
    color: {accent_color};
  }}

  /* Main Content Area */
  .content-area {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin: 30px 0;
    z-index: 10;
  }}

  /* Cover Slide Styling */
  .cover-card {{
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}

  .tag-label {{
    display: inline-block;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: {accent_color};
    margin-bottom: 25px;
  }}

  .title-cover {{
    font-size: 68px;
    font-weight: 900;
    line-height: 1.15;
    letter-spacing: -1.5px;
    color: {text_color};
    max-width: 900px;
    margin-bottom: 25px;
  }}

  .title-cover.single-title {{
    font-size: 52px;
    max-width: 760px;
    line-height: 1.25;
    margin-bottom: 24px;
  }}

  .title-cover .highlight {{
    color: {accent_color};
  }}

  .sub-cover {{
    font-family: 'Inter', sans-serif;
    font-size: 26px;
    font-weight: 500;
    color: {sub_color};
    max-width: 820px;
    line-height: 1.5;
    margin-bottom: 45px;
  }}

  .sub-cover.single-sub {{
    font-size: 22px;
    max-width: 700px;
    margin-bottom: 40px;
  }}

  .pill-cta {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: {btn_bg};
    color: {btn_color};
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 2px;
    padding: 20px 48px;
    border-radius: 999px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    cursor: pointer;
  }}

  /* Content / Breakdown Slide Styling */
  .content-card {{
    background: {card_bg};
    border: 1px solid {card_border};
    border-radius: 32px;
    padding: 60px 50px;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
    position: relative;
    overflow: hidden;
  }}

  .content-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: {accent_color};
  }}

  .card-title {{
    font-size: 48px;
    font-weight: 800;
    line-height: 1.2;
    letter-spacing: -0.8px;
    margin-bottom: 20px;
  }}

  .card-title .highlight {{
    color: {accent_color};
  }}

  .card-subtitle {{
    font-size: 24px;
    font-weight: 500;
    color: {sub_color};
    line-height: 1.45;
    margin-bottom: 35px;
  }}

  .items-list {{
    display: flex;
    flex-direction: column;
    gap: 18px;
  }}

  .item-row {{
    display: flex;
    align-items: center;
    gap: 20px;
    background: {row_bg};
    border: 1px solid {row_border};
    padding: 22px 26px;
    border-radius: 18px;
  }}

  .item-badge {{
    width: 38px;
    height: 38px;
    border-radius: 12px;
    background: rgba(249, 115, 22, 0.15);
    border: 1px solid rgba(249, 115, 22, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    color: {accent_color};
    font-size: 18px;
    font-weight: 800;
    flex-shrink: 0;
  }}

  .item-text {{
    font-size: 23px;
    font-weight: 600;
    color: {text_color};
    line-height: 1.35;
  }}

  /* Footer Section */
  .footer-section {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 25px;
    border-top: 1px solid {footer_border};
    width: 100%;
    z-index: 10;
  }}

  .footer-brand {{
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {text_color};
  }}

  .footer-handle {{
    font-size: 16px;
    font-weight: 600;
    color: {sub_color};
  }}

  .footer-handle span {{
    color: {accent_color};
  }}

  .swipe-note {{
    font-size: 17px;
    font-weight: 800;
    letter-spacing: 2px;
    color: {accent_color};
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 25px;
  }}
</style>
</head>
<body>
  <!-- Header Bar -->
  <div class="top-section">
    <div class="logo-container">
      {logo_img_tag}
    </div>
    {top_pill_html}
  </div>

  <!-- Content Area -->
  <div class="content-area">
    {content_body}
  </div>

  <!-- Footer Bar -->
  <div class="footer-section">
    <div class="footer-brand">{brand_name}</div>
    <div class="footer-handle">{handle} • <span>{website_domain}</span></div>
  </div>
</body>
</html>
"""

def render_kbd_carousel_slide(slide: dict, slide_num: int, total_slides: int, theme: str = None) -> str:
    """Renders slide HTML matching Known By Digital with active theme."""
    if not theme:
        theme = get_current_day_theme()
    t_cfg = THEME_CONFIGS.get(theme, THEME_CONFIGS["dark"])

    headline = slide.get("headline", "")
    subheadline = slide.get("subheadline", "")
    points = slide.get("points", [])
    slide_type = slide.get("type", "content")
    
    logo_base64 = get_theme_logo_base64(theme)
    if logo_base64:
        logo_img_tag = f'<img class="logo-img" src="data:image/png;base64,{logo_base64}" alt="Known By Digital" />'
    else:
        logo_img_tag = f'<div style="font-weight:900; font-size:22px; letter-spacing:2px; color:{t_cfg["text_color"]};">KNOWN BY <span style="color:{t_cfg["accent_color"]};">DIGITAL</span></div>'

    words = headline.split()
    if len(words) > 2:
        title_html = " ".join(words[:-1]) + f' <span class="highlight">{words[-1]}</span>'
    else:
        title_html = f'<span class="highlight">{headline}</span>'

    if total_slides > 1:
        top_pill_html = f'<div class="counter-pill"><span>{slide_num:02d}</span> / {total_slides:02d}</div>'
    else:
        top_pill_html = f'<div class="counter-pill"><span>2026</span> PLAYBOOK</div>'

    if total_slides == 1:
        content_body = f"""
        <div class="cover-card">
          <div class="tag-label">🔥 2026 STRATEGY INSIGHT</div>
          <h1 class="title-cover single-title">{title_html}</h1>
          <p class="sub-cover single-sub">{subheadline}</p>
          <div class="pill-cta">READ CAPTION FOR FULL BREAKDOWN ➔</div>
        </div>
        """
    elif slide_type == "cover" or slide_num == 1:
        content_body = f"""
        <div class="cover-card">
          <div class="tag-label">🔥 PROVEN STRATEGY</div>
          <h1 class="title-cover">{title_html}</h1>
          <p class="sub-cover">{subheadline}</p>
          <div class="pill-cta">SWIPE TO READ DETAILS ➔</div>
        </div>
        """
    elif slide_type == "cta" or slide_num == total_slides:
        content_body = f"""
        <div class="cover-card">
          <div class="tag-label">🚀 NEXT ACTIONABLE STEP</div>
          <h1 class="title-cover">Ready to Scale Your Brand in <span class="highlight">2026?</span></h1>
          <p class="sub-cover">{subheadline or 'Stop leaving revenue on the table. Let our team build your autonomous marketing engine.'}</p>
          <div class="pill-cta">DM 'SYSTEM' OR VISIT OUR WEBSITE</div>
        </div>
        """
    else:
        items_html = ""
        if points:
            items_html = '<div class="items-list">'
            for idx, pt in enumerate(points):
                items_html += f"""
                <div class="item-row">
                  <div class="item-badge">{idx+1:02d}</div>
                  <div class="item-text">{pt}</div>
                </div>
                """
            items_html += '</div>'

        content_body = f"""
        <div class="content-card">
          <h2 class="card-title">{title_html}</h2>
          <p class="card-subtitle">{subheadline}</p>
          {items_html}
          <div class="swipe-note">SWIPE FOR NEXT STEP ➔</div>
        </div>
        """

    return HTML_TEMPLATE_KBD_CAROUSEL.format(
        bg_color=t_cfg["bg_color"],
        bg_gradient=t_cfg["bg_gradient"],
        text_color=t_cfg["text_color"],
        sub_color=t_cfg["sub_color"],
        accent_color=t_cfg["accent_color"],
        card_bg=t_cfg["card_bg"],
        card_border=t_cfg["card_border"],
        row_bg=t_cfg["row_bg"],
        row_border=t_cfg["row_border"],
        pill_bg=t_cfg["pill_bg"],
        pill_border=t_cfg["pill_border"],
        pill_text=t_cfg["pill_text"],
        btn_bg=t_cfg["btn_bg"],
        btn_color=t_cfg["btn_color"],
        footer_border=t_cfg["footer_border"],
        logo_img_tag=logo_img_tag,
        top_pill_html=top_pill_html,
        content_body=content_body,
        brand_name=BRAND["name"],
        handle=BRAND["handle"],
        website_domain=BRAND["website"].replace("https://", "")
    )

from playwright.sync_api import sync_playwright

def render_html_to_image(html_content: str, output_path: str, width: int = 1080, height: int = 1350):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        page.set_content(html_content, wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.screenshot(path=output_path, type="png")
        browser.close()
    return output_path

def generate_pro_carousel_slides(carousel_data: dict, prefix: str = "kbd_carousel", theme: str = None) -> list:
    if not theme:
        theme = get_current_day_theme()
    slides = carousel_data.get("slides", [])
    output_files = []
    total_slides = len(slides)

    for idx, slide in enumerate(slides):
        slide_num = idx + 1
        html = render_kbd_carousel_slide(slide, slide_num, total_slides, theme=theme)
        out_file = str(MEDIA_DIR / f"{prefix}_slide_{slide_num}.png")
        render_html_to_image(html, out_file, width=1080, height=1350)
        output_files.append(out_file)

    return output_files

HTML_TEMPLATE_KBD_SINGLE_POST = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800;900&family=Inter:wght@500;600;700&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 1080px;
    height: 1080px;
    background-color: {bg_color};
    background-image: {bg_gradient};
    color: {text_color};
    font-family: 'Plus Jakarta Sans', sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    padding: 80px 140px;
    overflow: hidden;
    position: relative;
    text-align: center;
  }}
  .top-section {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    z-index: 10;
  }}
  .logo-img {{ height: 50px; width: auto; object-fit: contain; }}
  .tag-pill {{
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 2px;
    color: {sub_color};
    background: {pill_bg};
    border: 1px solid {pill_border};
    padding: 9px 20px;
    border-radius: 999px;
  }}
  .tag-pill span {{ color: {accent_color}; }}
  .center-content {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    max-width: 800px;
    margin: auto;
    z-index: 10;
  }}
  .badge-label {{
    display: inline-block;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 3px;
    color: {accent_color};
    text-transform: uppercase;
    margin-bottom: 25px;
  }}
  .hero-title {{
    font-size: 48px;
    font-weight: 800;
    line-height: 1.25;
    letter-spacing: -1.2px;
    color: {text_color};
    margin-bottom: 25px;
    max-width: 780px;
  }}
  .hero-title .highlight {{
    color: {accent_color};
  }}
  .hero-sub {{
    font-family: 'Inter', sans-serif;
    font-size: 22px;
    font-weight: 500;
    color: {sub_color};
    line-height: 1.55;
    max-width: 720px;
    margin-bottom: 35px;
  }}
  .pill-cta {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: {btn_bg};
    color: {btn_color};
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 2px;
    padding: 18px 44px;
    border-radius: 999px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
  }}
  .footer-section {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    border-top: 1px solid {footer_border};
    padding-top: 25px;
    z-index: 10;
  }}
  .footer-brand {{ font-size: 18px; font-weight: 800; color: {text_color}; }}
  .footer-handle {{ font-size: 16px; font-weight: 600; color: {sub_color}; }}
  .footer-handle span {{ color: {accent_color}; }}
</style>
</head>
<body>
  <div class="top-section">
    {logo_img_tag}
    <div class="tag-pill"><span>AI</span> STRATEGY</div>
  </div>
  <div class="center-content">
    <div class="badge-label">🔥 PROVEN SYSTEM</div>
    <h1 class="hero-title">{title_html}</h1>
    <p class="hero-sub">{subheadline}</p>
    <div class="pill-cta">READ CAPTION FOR FULL SOP ➔</div>
  </div>
  <div class="footer-section">
    <div class="footer-brand">{brand_name}</div>
    <div class="footer-handle">{handle} • <span>{website_domain}</span></div>
  </div>
</body>
</html>
"""

def render_kbd_single_post_html(post_data: dict, theme: str = None) -> str:
    if not theme:
        theme = get_current_day_theme()
    t_cfg = THEME_CONFIGS.get(theme, THEME_CONFIGS["dark"])
    
    headline = post_data.get("headline", "Stop Doing This If Your Content Isn't Converting")
    subtitle = post_data.get("image_card_subtitle", post_data.get("image_card_title", "5 Fixes Every E-commerce and Tech Brand Needs in 2026"))

    logo_base64 = get_theme_logo_base64(theme)
    if logo_base64:
        logo_img_tag = f'<img class="logo-img" src="data:image/png;base64,{logo_base64}" alt="Known By Digital" />'
    else:
        logo_img_tag = f'<div style="font-weight:900; font-size:22px; letter-spacing:2px; color:{t_cfg["text_color"]};">KNOWN BY <span style="color:{t_cfg["accent_color"]};">DIGITAL</span></div>'

    words = headline.split()
    if len(words) > 2:
        title_html = " ".join(words[:-1]) + f' <span class="highlight">{words[-1]}</span>'
    else:
        title_html = f'<span class="highlight">{headline}</span>'

    return HTML_TEMPLATE_KBD_SINGLE_POST.format(
        bg_color=t_cfg["bg_color"],
        bg_gradient=t_cfg["bg_gradient"],
        text_color=t_cfg["text_color"],
        sub_color=t_cfg["sub_color"],
        accent_color=t_cfg["accent_color"],
        card_bg=t_cfg["card_bg"],
        card_border=t_cfg["card_border"],
        pill_bg=t_cfg["pill_bg"],
        pill_border=t_cfg["pill_border"],
        btn_bg=t_cfg["btn_bg"],
        btn_color=t_cfg["btn_color"],
        footer_border=t_cfg["footer_border"],
        logo_img_tag=logo_img_tag,
        title_html=title_html,
        subheadline=subtitle,
        brand_name=BRAND["name"],
        handle=BRAND["handle"],
        website_domain=BRAND["website"].replace("https://", "")
    )

def generate_pro_single_post_image(post_data: dict, output_filename: str = "kbd_single_post.png", theme: str = None) -> str:
    if not theme:
        theme = get_current_day_theme()
    html = render_kbd_single_post_html(post_data, theme=theme)
    out_file = str(MEDIA_DIR / output_filename)
    render_html_to_image(html, out_file, width=1080, height=1080)
    return out_file

if __name__ == "__main__":
    th = get_current_day_theme()
    print(f"Current Day Theme: {th}")
