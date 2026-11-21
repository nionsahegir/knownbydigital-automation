import os
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

def get_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

logo_dark_b64 = get_b64("kbd_logo_dark_theme.png")
logo_light_b64 = get_b64("kbd_logo_light_theme.png")
logo_white_b64 = get_b64("kbd_logo_white_pure.png")

def make_html(theme):
    if theme == 'dark':
        bg = '#0A0A0A'
        bg_grad = 'radial-gradient(circle at 50% 10%, rgba(249, 115, 22, 0.08) 0%, transparent 60%)'
        color = '#FFFFFF'
        sub_color = '#A3A3A3'
        accent = '#F97316'
        card_bg = '#141414'
        card_border = '#262626'
        pill_bg = '#1F1F1F'
        pill_border = '#333333'
        logo_data = logo_dark_b64
        btn_bg = 'linear-gradient(135deg, #F97316 0%, #EA580C 100%)'
        btn_color = '#000000'
    elif theme == 'light':
        bg = '#FAFAFA'
        bg_grad = 'radial-gradient(circle at 50% 10%, rgba(249, 115, 22, 0.05) 0%, transparent 60%)'
        color = '#0F172A'
        sub_color = '#475569'
        accent = '#EA580C'
        card_bg = '#FFFFFF'
        card_border = '#E2E8F0'
        pill_bg = '#F1F5F9'
        pill_border = '#E2E8F0'
        logo_data = logo_light_b64
        btn_bg = 'linear-gradient(135deg, #EA580C 0%, #C2410C 100%)'
        btn_color = '#FFFFFF'
    else:  # orange
        bg = '#EA580C'
        bg_grad = 'radial-gradient(circle at 50% 0%, #FB923C 0%, #EA580C 100%)'
        color = '#FFFFFF'
        sub_color = 'rgba(255, 255, 255, 0.92)'
        accent = '#0A0A0A'
        card_bg = 'rgba(0, 0, 0, 0.15)'
        card_border = 'rgba(255, 255, 255, 0.25)'
        pill_bg = 'rgba(0, 0, 0, 0.25)'
        pill_border = 'rgba(255, 255, 255, 0.35)'
        logo_data = logo_white_b64
        btn_bg = '#0A0A0A'
        btn_color = '#FFFFFF'

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800;900&family=Inter:wght@500;600;700&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    width: 1080px; height: 1350px;
    background-color: {bg};
    background-image: {bg_grad};
    color: {color};
    font-family: 'Plus Jakarta Sans', sans-serif;
    display: flex; flex-direction: column; justify-content: space-between;
    padding: 60px 80px;
  }}
  .top {{ display: flex; justify-content: space-between; align-items: center; }}
  .logo {{ height: 55px; width: auto; object-fit: contain; }}
  .pill {{
    font-family: 'Inter', sans-serif; font-size: 16px; font-weight: 700;
    letter-spacing: 2px; color: {sub_color}; background: {pill_bg};
    border: 1px solid {pill_border}; padding: 10px 22px; border-radius: 999px;
  }}
  .content {{ flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }}
  .badge {{ font-size: 16px; font-weight: 800; letter-spacing: 3px; color: {accent}; margin-bottom: 25px; }}
  .title {{ font-size: 68px; font-weight: 900; line-height: 1.15; letter-spacing: -1.5px; max-width: 900px; margin-bottom: 25px; }}
  .title span {{ color: {accent}; }}
  .sub {{ font-family: 'Inter', sans-serif; font-size: 26px; font-weight: 500; color: {sub_color}; max-width: 820px; line-height: 1.5; margin-bottom: 45px; }}
  .btn {{ font-size: 20px; font-weight: 800; letter-spacing: 2px; background: {btn_bg}; color: {btn_color}; padding: 18px 45px; border-radius: 999px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
  .footer {{ display: flex; justify-content: space-between; align-items: center; border-top: 1px solid {card_border}; padding-top: 25px; }}
  .brand {{ font-size: 20px; font-weight: 800; color: {color}; }}
  .handle {{ font-size: 18px; font-weight: 600; color: {sub_color}; }}
</style>
</head>
<body>
  <div class="top">
    <img class="logo" src="data:image/png;base64,{logo_data}" />
    <div class="pill">01 / 05</div>
  </div>
  <div class="content">
    <div class="badge">🔥 PROVEN STRATEGY</div>
    <h1 class="title">The 2026 Shopify Tech <span>Stack</span></h1>
    <p class="sub">How top 7-figure brands cut operations overhead by 40% with autonomous AI agents.</p>
    <div class="btn">SWIPE TO READ DETAILS ➔</div>
  </div>
  <div class="footer">
    <div class="brand">Known By Digital</div>
    <div class="handle">@knownbydigital • knownbydigital.com</div>
  </div>
</body>
</html>"""

out_dir = Path("preview_themes")
out_dir.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1350})
    for th in ["dark", "light", "orange"]:
        html = make_html(th)
        page.set_content(html, wait_until="networkidle")
        p_path = str(out_dir / f"theme_{th}.png")
        page.screenshot(path=p_path)
        print(f"Rendered: {p_path}")
    browser.close()
