import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from html_renderer import THEME_CONFIGS, get_current_day_theme, get_theme_logo_base64
from config import BRAND, MEDIA_DIR

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent

STORY_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800;900&family=Inter:wght@500;600;700;800&display=swap');
  
  * {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }}

  body {{
    width: 1080px;
    height: 1920px;
    background-color: {bg_color};
    background-image: {bg_gradient};
    color: {text_color};
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    padding: 180px 70px 180px 70px; /* Safe bounds away from Story header and reply bar */
    position: relative;
    overflow: hidden;
  }}

  /* Top Story Header */
  .story-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    max-width: 940px;
    z-index: 20;
  }}

  .story-brand {{
    display: flex;
    align-items: center;
    gap: 16px;
  }}

  .logo-img {{
    height: 48px;
    width: auto;
    object-fit: contain;
    filter: drop-shadow(0 4px 15px rgba(249, 115, 22, 0.4));
  }}

  .brand-text {{
    font-size: 24px;
    font-weight: 900;
    letter-spacing: 2px;
    color: {text_color};
  }}

  .brand-text span {{
    color: {accent_color};
  }}

  .story-badge {{
    background: {pill_bg};
    border: 1.5px solid {pill_border};
    padding: 9px 24px;
    border-radius: 999px;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 800;
    color: {pill_text};
    letter-spacing: 2px;
    text-transform: uppercase;
  }}

  /* Main Interactive Story Card */
  .story-card {{
    width: 100%;
    max-width: 940px;
    background: {card_bg};
    border: 2px solid {card_border};
    border-radius: 40px;
    box-shadow: 0 35px 80px rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(30px);
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 60px 48px;
    gap: 30px;
    z-index: 20;
  }}

  .story-tag {{
    background: {pill_bg};
    border: 1px solid {pill_border};
    color: {pill_text};
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 2.5px;
    padding: 10px 24px;
    border-radius: 999px;
    text-transform: uppercase;
  }}

  .story-title {{
    font-size: 50px;
    font-weight: 900;
    line-height: 1.18;
    letter-spacing: -2px;
    color: {text_color};
  }}

  .story-title .highlight {{
    color: {accent_color};
  }}

  /* Interactive Poll / Choice UI Widget */
  .story-poll {{
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin: 10px 0;
  }}

  .poll-option {{
    width: 100%;
    background: {row_bg};
    border: 1.5px solid {row_border};
    border-radius: 22px;
    padding: 22px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    text-align: left;
    transition: all 0.2s ease;
  }}

  .poll-option.highlighted {{
    background: {pill_bg};
    border: 2px solid {accent_color};
    box-shadow: 0 0 25px rgba(0, 0, 0, 0.2);
  }}

  .poll-label {{
    font-size: 20px;
    font-weight: 800;
    color: {text_color};
  }}

  .poll-pct {{
    font-size: 22px;
    font-weight: 900;
    color: {accent_color};
  }}

  /* Bottom Sticker Action */
  .story-action-sticker {{
    display: inline-flex;
    align-items: center;
    gap: 12px;
    background: {btn_bg};
    color: {btn_color};
    font-size: 20px;
    font-weight: 900;
    letter-spacing: 2px;
    padding: 18px 46px;
    border-radius: 999px;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.35);
    text-transform: uppercase;
  }}

  /* Story Footer Branding */
  .story-footer {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    max-width: 940px;
    border-top: 1px solid {footer_border};
    padding-top: 25px;
    z-index: 20;
  }}

  .footer-handle {{
    font-size: 18px;
    font-weight: 800;
    color: {sub_color};
  }}

  .footer-url {{
    font-size: 18px;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
    color: {sub_color};
  }}

  .footer-url span {{
    color: {accent_color};
  }}
</style>
</head>
<body>

  <!-- Story Top Header -->
  <div class="story-header">
    <div class="story-brand">
      {logo_img_tag}
      <div class="brand-text">KNOWN BY <span>DIGITAL</span></div>
    </div>
    <div class="story-badge">NEW REEL LIVE ⚡</div>
  </div>

  <!-- Main Interactive Story Card -->
  <div class="story-card">
    <div class="story-tag">{tag}</div>
    
    <h1 class="story-title">{headline_html}</h1>

    <!-- Simulated Interactive Story Poll Widget -->
    <div class="story-poll">
      <div class="poll-option">
        <span class="poll-label">{poll_opt_a}</span>
        <span class="poll-pct">22%</span>
      </div>
      <div class="poll-option highlighted">
        <span class="poll-label">{poll_opt_b}</span>
        <span class="poll-pct">78% ✓</span>
      </div>
    </div>

    <!-- Instagram Interactive Action Sticker -->
    <div class="story-action-sticker">
      {action_sticker}
    </div>
  </div>

  <!-- Story Bottom Footer -->
  <div class="story-footer">
    <div class="footer-handle">{handle}</div>
    <div class="footer-url"><span>KBD</span> SYSTEMS • {website_domain}</div>
  </div>

</body>
</html>
"""

def generate_pro_story_image(story_data: dict = None, output_filename: str = "story.jpg", theme: str = None) -> str:
    """Generates an agency-grade 1080x1920 Instagram Story poll graphic in the active brand theme."""
    if not theme:
        theme = get_current_day_theme()
    t_cfg = THEME_CONFIGS.get(theme, THEME_CONFIGS["dark"])

    if not story_data:
        story_data = {}

    tag = story_data.get("tag", "⚡ TODAY'S GROWTH POLL")
    headline = story_data.get("headline", "How Does Your Team Qualify Inbound Deals?")
    poll_opt_a = story_data.get("poll_opt_a", "A) Manual Rep Follow-up (15m+ Delay)")
    poll_opt_b = story_data.get("poll_opt_b", "B) Autonomous AI Agent (4-Sec Intake)")
    action_sticker = story_data.get("action_sticker", "TAP TO WATCH NEW REEL ➔")

    words = headline.split()
    if len(words) > 3:
        headline_html = " ".join(words[:-2]) + f' <span class="highlight">{" ".join(words[-2:])}</span>'
    elif len(words) > 1:
        headline_html = " ".join(words[:-1]) + f' <span class="highlight">{words[-1]}</span>'
    else:
        headline_html = f'<span class="highlight">{headline}</span>'

    logo_base64 = get_theme_logo_base64(theme)
    if logo_base64:
        logo_img_tag = f'<img class="logo-img" src="data:image/png;base64,{logo_base64}" alt="Known By Digital" />'
    else:
        logo_img_tag = f'<div style="font-size:24px; font-weight:900; color:{t_cfg["accent_color"]};">KBD</div>'

    html_content = STORY_HTML_TEMPLATE.format(
        bg_color=t_cfg["bg_color"],
        bg_gradient=t_cfg["bg_gradient"],
        text_color=t_cfg["text_color"],
        sub_color=t_cfg["sub_color"],
        accent_color=t_cfg["accent_color"],
        card_bg=t_cfg["card_bg"],
        card_border=t_cfg["card_border"],
        row_bg=t_cfg.get("row_bg", "rgba(0,0,0,0.1)"),
        row_border=t_cfg.get("row_border", "rgba(255,255,255,0.1)"),
        pill_bg=t_cfg["pill_bg"],
        pill_border=t_cfg["pill_border"],
        pill_text=t_cfg["pill_text"],
        btn_bg=t_cfg["btn_bg"],
        btn_color=t_cfg["btn_color"],
        footer_border=t_cfg["footer_border"],
        logo_img_tag=logo_img_tag,
        tag=tag,
        headline_html=headline_html,
        poll_opt_a=poll_opt_a,
        poll_opt_b=poll_opt_b,
        action_sticker=action_sticker,
        handle=BRAND["handle"],
        website_domain=BRAND["website"].replace("https://", "")
    )

    out_path = MEDIA_DIR / output_filename
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.set_content(html_content, wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.screenshot(path=str(out_path), type="jpeg", quality=98)
        browser.close()

    print(f"[Story Engine] ({theme.upper()} Theme) Instagram Story image created at: {out_path}")
    return str(out_path)

if __name__ == "__main__":
    for th in ["dark", "orange", "light"]:
        s = generate_pro_story_image(output_filename=f"test_story_{th}.jpg", theme=th)
        print("Story created:", s)
