import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from html_renderer import THEME_CONFIGS, get_current_day_theme, get_theme_logo_base64
from config import BRAND, MEDIA_DIR

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent

REEL_COVER_HTML_TEMPLATE = """<!DOCTYPE html>
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
    padding: 90px 65px;
    position: relative;
    overflow: hidden;
  }}

  /* Top 9:16 Area */
  .top-branding {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    max-width: 950px;
    z-index: 30;
  }}

  .logo-wrap {{
    display: flex;
    align-items: center;
    gap: 15px;
  }}

  .logo-img {{
    height: 48px;
    width: auto;
    object-fit: contain;
    filter: drop-shadow(0 4px 15px rgba(249, 115, 22, 0.4));
  }}

  .brand-text {{
    font-size: 26px;
    font-weight: 900;
    letter-spacing: 2px;
    color: {text_color};
  }}

  .brand-text span {{
    color: {accent_color};
  }}

  .top-pill {{
    background: {pill_bg};
    border: 1.5px solid {pill_border};
    padding: 10px 24px;
    border-radius: 999px;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 800;
    color: {pill_text};
    letter-spacing: 2px;
    text-transform: uppercase;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }}

  /* CRITICAL: Center 1080x1080 Square Safe Zone (Visible on 1:1 Profile Grid Crop) */
  .grid-safe-zone {{
    width: 950px;
    height: 980px;
    background: {card_bg};
    border: 2px solid {card_border};
    border-radius: 44px;
    box-shadow: 0 35px 80px rgba(0, 0, 0, 0.45);
    backdrop-filter: blur(30px);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    padding: 55px 48px;
    text-align: center;
    position: relative;
    z-index: 20;
  }}

  .category-badge {{
    background: {pill_bg};
    border: 1px solid {pill_border};
    color: {pill_text};
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 2.5px;
    padding: 10px 26px;
    border-radius: 999px;
    text-transform: uppercase;
  }}

  .hero-headline {{
    font-size: 58px;
    font-weight: 900;
    line-height: 1.15;
    letter-spacing: -2px;
    color: {text_color};
    margin: 10px 0;
  }}

  .hero-headline .highlight {{
    color: {accent_color};
  }}

  /* Vector AI Robot Mascot & Graphics */
  .mascot-stage {{
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 10px 0;
  }}

  .mascot-ring-glow {{
    position: absolute;
    width: 280px;
    height: 280px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(249, 115, 22, 0.25) 0%, transparent 70%);
    filter: blur(20px);
    z-index: 1;
  }}

  .mascot-svg {{
    position: relative;
    z-index: 2;
    filter: drop-shadow(0 15px 30px rgba(0, 0, 0, 0.4));
  }}

  .cta-watch-btn {{
    background: {btn_bg};
    color: {btn_color};
    padding: 20px 48px;
    border-radius: 999px;
    font-size: 20px;
    font-weight: 900;
    letter-spacing: 2px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  /* Bottom 9:16 Area */
  .bottom-branding {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    max-width: 950px;
    border-top: 1px solid {footer_border};
    padding-top: 25px;
    z-index: 30;
  }}

  .bottom-left {{
    font-size: 20px;
    font-weight: 800;
    color: {sub_color};
  }}

  .bottom-right {{
    font-size: 19px;
    font-weight: 700;
    color: {sub_color};
  }}

  .bottom-right span {{
    color: {accent_color};
  }}
</style>
</head>
<body>

  <!-- Top 9:16 Section -->
  <div class="top-branding">
    <div class="logo-wrap">
      {logo_img_tag}
      <div class="brand-text">KNOWN BY <span>DIGITAL</span></div>
    </div>
    <div class="top-pill">REEL EXCLUSIVE ⚡</div>
  </div>

  <!-- Center 1080x1080 Grid Safe Zone (Appears on Profile Grid) -->
  <div class="grid-safe-zone">
    <div class="category-badge">● B2B REVENUE ARCHITECTURE</div>
    
    <h1 class="hero-headline">{headline_html}</h1>

    <!-- Vector AI Robot Mascot -->
    <div class="mascot-stage">
      <div class="mascot-ring-glow"></div>
      <svg width="200" height="210" viewBox="0 0 200 210" fill="none" class="mascot-svg" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="c-body" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#1E293B" />
            <stop offset="100%" stop-color="#0F172A" />
          </linearGradient>
          <linearGradient id="c-orange" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#F97316" />
            <stop offset="100%" stop-color="#EA580C" />
          </linearGradient>
          <filter id="c-glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="8" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>
        
        <!-- Antenna -->
        <path d="M100 24 L100 42" stroke="#F97316" stroke-width="4" stroke-linecap="round"/>
        <circle cx="100" cy="18" r="7" fill="#F97316" filter="url(#c-glow)"/>
        
        <!-- Head -->
        <rect x="42" y="42" width="116" height="86" rx="38" fill="url(#c-body)" stroke="#334155" stroke-width="3"/>
        
        <!-- Visor Face -->
        <rect x="56" y="58" width="88" height="46" rx="20" fill="#030712" stroke="#0EA5E9" stroke-width="2"/>
        
        <!-- Glowing Cyan Eyes -->
        <circle cx="80" cy="81" r="9" fill="#00F0FF" filter="url(#c-glow)"/>
        <circle cx="80" cy="81" r="3" fill="#FFFFFF"/>
        <circle cx="120" cy="81" r="9" fill="#00F0FF" filter="url(#c-glow)"/>
        <circle cx="120" cy="81" r="3" fill="#FFFFFF"/>
        
        <!-- Ears -->
        <rect x="32" y="68" width="10" height="28" rx="5" fill="#F97316"/>
        <rect x="158" y="68" width="10" height="28" rx="5" fill="#F97316"/>
        
        <!-- Neck -->
        <ellipse cx="100" cy="136" rx="22" ry="6" fill="#1E293B" stroke="#475569" stroke-width="2"/>
        
        <!-- Body Chassis -->
        <path d="M58 144 C58 144 75 140 100 140 C125 140 142 144 142 144 C150 152 154 175 148 200 C144 208 132 210 100 210 C68 210 56 208 52 200 C46 175 50 152 58 144 Z" fill="url(#c-body)" stroke="#334155" stroke-width="3"/>
        
        <!-- Glowing Reactor Core -->
        <circle cx="100" cy="176" r="17" fill="#0F172A" stroke="#F97316" stroke-width="2.5"/>
        <circle cx="100" cy="176" r="9" fill="url(#c-orange)" filter="url(#c-glow)"/>
        <path d="M100 168 L100 184 M92 176 L108 176" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </div>

    <!-- High-Converting CTA Button -->
    <div class="cta-watch-btn">
      WATCH REEL ➔
    </div>
  </div>

  <!-- Bottom 9:16 Section -->
  <div class="bottom-branding">
    <div class="bottom-left">{handle}</div>
    <div class="bottom-right">VISIT <span>{website_domain}</span></div>
  </div>

</body>
</html>
"""

def generate_pro_reel_cover_image(reel_data: dict, output_filename: str = "reel_cover.jpg", theme: str = None) -> str:
    """Generates a dedicated 1080x1920 Single-Post-quality cover image for Instagram Reels with 1:1 Grid Safe Zone in the active brand theme."""
    if not theme:
        theme = get_current_day_theme()
    t_cfg = THEME_CONFIGS.get(theme, THEME_CONFIGS["dark"])

    hook = reel_data.get("hook_3s", "Stop Chasing Leads Manually")

    # Format Headline with gradient highlight on last 1-2 words
    words = hook.split()
    if len(words) > 3:
        headline_html = " ".join(words[:-2]) + f' <span class="highlight">{" ".join(words[-2:])}</span>'
    elif len(words) > 1:
        headline_html = " ".join(words[:-1]) + f' <span class="highlight">{words[-1]}</span>'
    else:
        headline_html = f'<span class="highlight">{hook}</span>'

    logo_base64 = get_theme_logo_base64(theme)
    if logo_base64:
        logo_img_tag = f'<img class="logo-img" src="data:image/png;base64,{logo_base64}" alt="Known By Digital" />'
    else:
        logo_img_tag = f'<div style="font-size:24px; font-weight:900; color:{t_cfg["accent_color"]};">KBD</div>'

    html_content = REEL_COVER_HTML_TEMPLATE.format(
        bg_color=t_cfg["bg_color"],
        bg_gradient=t_cfg["bg_gradient"],
        text_color=t_cfg["text_color"],
        sub_color=t_cfg["sub_color"],
        accent_color=t_cfg["accent_color"],
        card_bg=t_cfg["card_bg"],
        card_border=t_cfg["card_border"],
        pill_bg=t_cfg["pill_bg"],
        pill_border=t_cfg["pill_border"],
        pill_text=t_cfg["pill_text"],
        btn_bg=t_cfg["btn_bg"],
        btn_color=t_cfg["btn_color"],
        footer_border=t_cfg["footer_border"],
        logo_img_tag=logo_img_tag,
        headline_html=headline_html,
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

    print(f"[Reel Cover Engine] ({theme.upper()} Theme) Dedicated high-converting cover saved at: {out_path}")
    return str(out_path)

if __name__ == "__main__":
    for th in ["dark", "orange", "light"]:
        c = generate_pro_reel_cover_image({"hook_3s": "Stop Chasing Leads Manually"}, f"test_cover_{th}.jpg", theme=th)
        print("Dedicated Cover Created:", c)
