import os
import sys
import json
import time
import asyncio
import subprocess
from pathlib import Path
import imageio_ffmpeg
from playwright.sync_api import sync_playwright
import edge_tts
from html_renderer import THEME_CONFIGS, get_current_day_theme, get_theme_logo_base64
from reel_cover_engine import generate_pro_reel_cover_image
from config import BRAND, MEDIA_DIR

FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
BASE_DIR = Path(__file__).resolve().parent

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# The Full-Height Silicon Valley SaaS Window Animated HTML5 Canvas (1080x1920)
CANVA_REEL_ANIMATION_HTML = """<!DOCTYPE html>
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
    background-image: 
      radial-gradient(circle at 50% 8%, rgba(249, 115, 22, 0.22) 0%, transparent 60%),
      radial-gradient(circle at 50% 92%, rgba(234, 88, 12, 0.18) 0%, transparent 60%),
      radial-gradient(rgba(249, 115, 22, 0.15) 1.5px, transparent 1.5px);
    background-size: auto, auto, 36px 36px;
    color: {text_color};
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    padding: 85px 65px 80px 65px;
    overflow: hidden;
    position: relative;
  }}

  /* Top Animated Progress Bar */
  .top-progress-container {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 12px;
    background: rgba(255, 255, 255, 0.1);
    z-index: 100;
  }}

  .top-progress-bar {{
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #F97316, #EA580C, #FB923C);
    box-shadow: 0 0 20px #F97316;
    animation: progressFill {total_duration}s linear forwards;
  }}

  @keyframes progressFill {{
    from {{ width: 0%; }}
    to {{ width: 100%; }}
  }}

  /* Top Brand Header Bar */
  .header-brand {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    max-width: 950px;
    z-index: 30;
  }}

  .brand-logo-container {{
    display: flex;
    align-items: center;
    gap: 15px;
  }}

  .logo-img {{
    height: 48px;
    width: auto;
    object-fit: contain;
    filter: drop-shadow(0 4px 12px rgba(0,0,0,0.3));
  }}

  .brand-logo-text {{
    font-size: 26px;
    font-weight: 900;
    letter-spacing: 2.5px;
    color: {text_color};
  }}

  .brand-logo-text span {{
    color: #F97316;
  }}

  .hud-badge {{
    background: rgba(249, 115, 22, 0.15);
    border: 1.5px solid rgba(249, 115, 22, 0.4);
    padding: 9px 24px;
    border-radius: 999px;
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    font-weight: 800;
    color: #F97316;
    letter-spacing: 2px;
    text-transform: uppercase;
    box-shadow: 0 4px 20px rgba(249, 115, 22, 0.2);
  }}

  /* Full-Height SaaS Tech Window */
  .tech-window {{
    width: 100%;
    max-width: 950px;
    height: 1580px;
    background: {window_bg};
    border: 2px solid {window_border};
    border-radius: 40px;
    box-shadow: 0 35px 80px rgba(0, 0, 0, 0.8), 0 0 50px rgba(249, 115, 22, 0.16);
    backdrop-filter: blur(30px);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
    position: relative;
    z-index: 20;
  }}

  .window-titlebar {{
    height: 75px;
    background: rgba(255, 255, 255, 0.03);
    border-bottom: 1.5px solid rgba(255, 255, 255, 0.08);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 32px;
    flex-shrink: 0;
  }}

  .window-dots {{
    display: flex;
    gap: 11px;
  }}

  .dot {{
    width: 15px;
    height: 15px;
    border-radius: 50%;
  }}

  .dot-red {{ background: #EF4444; }}
  .dot-yellow {{ background: #F59E0B; }}
  .dot-green {{ background: #10B981; }}

  .window-url {{
    background: rgba(0, 0, 0, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 999px;
    padding: 7px 26px;
    font-size: 16px;
    font-family: 'Inter', sans-serif;
    color: #A3A3A3;
    letter-spacing: 1px;
  }}

  .window-url span {{
    color: #F97316;
    font-weight: 700;
  }}

  .window-status {{
    display: flex;
    align-items: center;
    gap: 9px;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 800;
    color: #10B981;
    letter-spacing: 1.5px;
  }}

  .status-pulse {{
    width: 11px;
    height: 11px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 12px #10B981;
    animation: pulseDot 2s infinite alternate;
  }}

  @keyframes pulseDot {{
    0% {{ transform: scale(0.9); opacity: 0.7; }}
    100% {{ transform: scale(1.2); opacity: 1; }}
  }}

  /* Scenes Container inside Window */
  .window-body-wrapper {{
    position: relative;
    width: 100%;
    flex: 1;
    overflow: hidden;
  }}

  .scene-slide {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: none;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    text-align: center;
    padding: 45px 44px;
    opacity: 0;
    transform: translateY(20px) scale(0.98);
    transition: opacity 0.25s ease-out, transform 0.25s ease-out;
  }}

  .scene-slide.visible {{
    display: flex;
  }}

  .scene-slide.active {{
    opacity: 1;
    transform: translateY(0) scale(1);
  }}

  /* 1. HUD Stats Bar (Top of Body) */
  .hud-stats-bar {{
    width: 100%;
    display: flex;
    justify-content: space-between;
    gap: 14px;
  }}

  .hud-stat-chip {{
    flex: 1;
    background: rgba(255, 255, 255, 0.04);
    border: 1.5px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 14px 18px;
    text-align: center;
  }}

  .hud-stat-label {{
    font-size: 13px;
    font-family: 'Inter', sans-serif;
    color: {sub_color};
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 4px;
  }}

  .hud-stat-val {{
    font-size: 27px;
    font-weight: 900;
    color: #F97316;
  }}

  /* Animated Vector AI Robot Mascot & Graphics */
  .ai-mascot-widget {{
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    margin: 8px 0;
  }}

  .mascot-stage {{
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 4px 0;
  }}

  .mascot-svg-anim {{
    animation: mascotBob 3.2s ease-in-out infinite alternate;
  }}

  @keyframes mascotBob {{
    0% {{ transform: translateY(0); }}
    100% {{ transform: translateY(-10px); }}
  }}

  .antenna-dot {{
    animation: antennaPulse 1.6s infinite alternate;
  }}

  @keyframes antennaPulse {{
    0% {{ opacity: 0.6; transform: scale(0.9); }}
    100% {{ opacity: 1; transform: scale(1.2); }}
  }}

  .core-dot {{
    animation: corePulse 1.8s ease-in-out infinite alternate;
  }}

  @keyframes corePulse {{
    0% {{ transform: scale(0.85); opacity: 0.7; }}
    100% {{ transform: scale(1.15); opacity: 1; }}
  }}

  .mascot-ring-glow {{
    position: absolute;
    width: 220px;
    height: 220px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(249, 115, 22, 0.22) 0%, transparent 70%);
    filter: blur(20px);
    z-index: 1;
  }}

  .mascot-hud-chip {{
    position: absolute;
    background: rgba(15, 23, 42, 0.9);
    border: 1.5px solid rgba(249, 115, 22, 0.45);
    border-radius: 999px;
    padding: 7px 16px;
    font-size: 13px;
    font-weight: 800;
    font-family: 'Inter', sans-serif;
    color: #F97316;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    z-index: 10;
  }}

  .chip-left {{
    left: -15px;
    top: 30px;
    border-color: #06B6D4;
    color: #06B6D4;
  }}

  .chip-right {{
    right: -15px;
    bottom: 25px;
    border-color: #10B981;
    color: #10B981;
  }}

  /* 2. Visual Illustration Widgets */
  /* Scene 1: Terminal Widget */
  .terminal-widget {{
    width: 100%;
    background: rgba(0, 0, 0, 0.45);
    border: 1.5px solid rgba(249, 115, 22, 0.3);
    border-radius: 28px;
    padding: 26px 30px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
    gap: 16px;
    text-align: left;
    margin: 15px 0;
  }}

  .terminal-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }}

  .terminal-tag {{
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #F97316;
    text-transform: uppercase;
  }}

  .terminal-time {{
    font-size: 13px;
    font-family: 'Inter', sans-serif;
    color: #737373;
    font-weight: 600;
  }}

  .terminal-item {{
    display: flex;
    align-items: center;
    gap: 18px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 18px;
    padding: 16px 20px;
  }}

  .terminal-icon {{
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: rgba(249, 115, 22, 0.15);
    border: 1px solid #F97316;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
  }}

  .terminal-text-main {{
    font-size: 19px;
    font-weight: 800;
    color: {text_color};
    margin-bottom: 2px;
  }}

  .terminal-text-sub {{
    font-size: 14px;
    color: {sub_color};
    font-weight: 500;
    font-family: 'Inter', sans-serif;
  }}

  .terminal-badge {{
    margin-left: auto;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid #10B981;
    color: #10B981;
    padding: 6px 16px;
    border-radius: 999px;
    font-size: 14px;
    font-weight: 800;
  }}

  /* Scene 2: Comparison Matrix */
  .comparison-widget {{
    width: 100%;
    background: rgba(0, 0, 0, 0.45);
    border: 1.5px solid rgba(249, 115, 22, 0.3);
    border-radius: 28px;
    padding: 24px 26px;
    display: flex;
    gap: 18px;
    margin: 15px 0;
  }}

  .comp-col {{
    flex: 1;
    border-radius: 20px;
    padding: 18px 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    text-align: left;
  }}

  .comp-col.bad {{
    background: rgba(239, 68, 68, 0.08);
    border: 1.5px solid rgba(239, 68, 68, 0.25);
  }}

  .comp-col.good {{
    background: rgba(249, 115, 22, 0.1);
    border: 1.5px solid rgba(249, 115, 22, 0.35);
  }}

  .comp-title {{
    font-size: 15px;
    font-weight: 900;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 4px;
  }}

  .comp-title.bad {{ color: #EF4444; }}
  .comp-title.good {{ color: #F97316; }}

  .comp-point {{
    font-size: 15px;
    font-weight: 700;
    font-family: 'Inter', sans-serif;
    color: {text_color};
    display: flex;
    align-items: center;
    gap: 10px;
  }}

  /* Scene 3: 3-Node Architecture Flowchart */
  .flowchart-widget {{
    width: 100%;
    background: rgba(0, 0, 0, 0.45);
    border: 1.5px solid rgba(249, 115, 22, 0.3);
    border-radius: 28px;
    padding: 24px 26px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    align-items: center;
    margin: 15px 0;
  }}

  .flow-node {{
    display: flex;
    align-items: center;
    gap: 16px;
    width: 100%;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 14px 20px;
    border-radius: 18px;
    font-size: 18px;
    font-weight: 800;
    color: {text_color};
    text-align: left;
  }}

  .flow-node.active {{
    background: rgba(249, 115, 22, 0.16);
    border: 2px solid #F97316;
    color: #F97316;
    box-shadow: 0 0 25px rgba(249, 115, 22, 0.3);
  }}

  .flow-icon {{
    font-size: 22px;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: rgba(255,255,255,0.06);
  }}

  .flow-arrow {{
    font-size: 20px;
    color: #F97316;
    font-weight: 900;
    line-height: 1;
  }}

  /* Scene 4: SVG Growth Chart */
  .chart-widget {{
    width: 100%;
    background: rgba(0, 0, 0, 0.45);
    border: 1.5px solid rgba(249, 115, 22, 0.3);
    border-radius: 28px;
    padding: 22px 28px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    margin: 15px 0;
  }}

  .chart-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
  }}

  .chart-tag {{
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #F97316;
    text-transform: uppercase;
  }}

  .chart-bars {{
    display: flex;
    align-items: flex-end;
    justify-content: space-around;
    height: 155px;
    padding-top: 15px;
    border-bottom: 2px solid rgba(255, 255, 255, 0.1);
  }}

  .bar-col {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    width: 65px;
  }}

  .bar-fill {{
    width: 100%;
    border-radius: 12px 12px 4px 4px;
    background: linear-gradient(180deg, #F97316 0%, rgba(249, 115, 22, 0.3) 100%);
    box-shadow: 0 0 15px rgba(249, 115, 22, 0.3);
  }}

  .bar-val {{
    font-size: 16px;
    font-weight: 900;
    color: #F97316;
  }}

  .bar-label {{
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: {sub_color};
  }}

  /* Scene 5: SOP Booking Modal */
  .cta-modal-widget {{
    width: 100%;
    background: rgba(0, 0, 0, 0.55);
    border: 2px solid #F97316;
    border-radius: 28px;
    padding: 28px 30px;
    box-shadow: 0 25px 60px rgba(249, 115, 22, 0.25);
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 14px;
    margin: 15px 0;
  }}

  .modal-badge {{
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #F97316;
    background: rgba(249, 115, 22, 0.15);
    border: 1px solid rgba(249, 115, 22, 0.4);
    padding: 6px 18px;
    border-radius: 999px;
  }}

  .modal-title {{
    font-size: 28px;
    font-weight: 900;
    color: {text_color};
  }}

  .modal-sub {{
    font-size: 18px;
    font-family: 'Inter', sans-serif;
    color: {sub_color};
    font-weight: 600;
    max-width: 600px;
  }}

  .pulsing-cta-btn {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #F97316 0%, #EA580C 100%);
    color: #000000;
    font-size: 22px;
    font-weight: 900;
    letter-spacing: 2px;
    padding: 18px 45px;
    border-radius: 999px;
    box-shadow: 0 12px 35px rgba(249, 115, 22, 0.5);
    text-transform: uppercase;
    animation: ctaPulse 1.8s infinite alternate;
    margin-top: 5px;
  }}

  @keyframes ctaPulse {{
    0% {{ transform: scale(1); box-shadow: 0 10px 25px rgba(249, 115, 22, 0.4); }}
    100% {{ transform: scale(1.04); box-shadow: 0 20px 45px rgba(249, 115, 22, 0.7); }}
  }}

  /* 3. Headlines & Typography */
  .text-block {{
    width: 100%;
    margin: 10px 0 20px 0;
  }}

  .hero-h1 {{
    font-size: 58px;
    font-weight: 900;
    line-height: 1.18;
    letter-spacing: -2px;
    margin-bottom: 14px;
    color: {text_color};
  }}

  .hero-h1 span {{
    color: #F97316;
    background: linear-gradient(135deg, #F97316 0%, #FB923C 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}

  .hero-p {{
    font-size: 23px;
    color: {sub_color};
    line-height: 1.5;
    max-width: 820px;
    font-weight: 500;
    margin: auto;
    font-family: 'Inter', sans-serif;
  }}

  /* 4. Bottom Feature Badges */
  .feature-tags-row {{
    display: flex;
    gap: 14px;
    justify-content: center;
    width: 100%;
    flex-wrap: wrap;
  }}

  .feat-tag {{
    background: rgba(249, 115, 22, 0.12);
    border: 1.5px solid rgba(249, 115, 22, 0.35);
    color: #F97316;
    font-size: 17px;
    font-weight: 800;
    padding: 10px 24px;
    border-radius: 999px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  }}

  /* Window Footer Bar */
  .window-footer {{
    height: 65px;
    background: rgba(0, 0, 0, 0.45);
    border-top: 1.5px solid rgba(255, 255, 255, 0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #737373;
    flex-shrink: 0;
  }}

  .window-footer span {{
    color: #F97316;
  }}
</style>
</head>
<body>
  <!-- Top Progress Bar -->
  <div class="top-progress-container">
    <div class="top-progress-bar"></div>
  </div>

  <!-- Header Brand Bar -->
  <div class="header-brand">
    <div class="brand-logo-container">
      {logo_html}
    </div>
    <div class="hud-badge">⚡ 2026 ARCHITECTURE</div>
  </div>

  <!-- Central Full-Height SaaS Tech Window -->
  <div class="tech-window">
    <div class="window-titlebar">
      <div class="window-dots">
        <div class="dot dot-red"></div>
        <div class="dot dot-yellow"></div>
        <div class="dot dot-green"></div>
      </div>
      <div class="window-url">app.knownbydigital.com/<span id="window-url-path">revenue-engine</span></div>
      <div class="window-status">
        <div class="status-pulse"></div> LIVE 24/7
      </div>
    </div>

    <div class="window-body-wrapper">
      {scenes_html}
    </div>

    <div class="window-footer">
      KNOWN BY DIGITAL SYSTEM • <span>99.9% UPTIME</span> • ENCRYPTED 256-BIT
    </div>
  </div>

  <script>
    // Smooth Javascript Scene Switcher synced to duration with zero ghost overlap
    const scenes = document.querySelectorAll('.scene-slide');
    const totalScenes = scenes.length;
    const totalDurationMs = {total_duration_ms};
    const sceneTime = totalDurationMs / totalScenes;
    const urlSpan = document.getElementById('window-url-path');

    const urls = [
      "revenue-engine",
      "conversion-audit",
      "pipeline-flow",
      "growth-metrics",
      "claim-sop"
    ];

    let currentIndex = 0;
    scenes[0].classList.add('visible', 'active');

    const interval = setInterval(() => {{
      if (currentIndex >= totalScenes - 1) {{
        clearInterval(interval);
        return;
      }}

      const prev = scenes[currentIndex];
      prev.classList.remove('active');
      setTimeout(() => {{
        prev.classList.remove('visible');
      }}, 260);

      currentIndex++;
      if (urlSpan && urls[currentIndex]) {{
        urlSpan.innerText = urls[currentIndex];
      }}

      const next = scenes[currentIndex];
      next.classList.add('visible');
      requestAnimationFrame(() => {{
        requestAnimationFrame(() => {{
          next.classList.add('active');
        }});
      }});
    }}, sceneTime);
  </script>
</body>
</html>
"""

def generate_canva_reel_html(scenes_data: list, total_duration_seconds: float, theme: str = "dark") -> str:
    t_cfg = THEME_CONFIGS.get(theme, THEME_CONFIGS["dark"])
    logo_b64 = get_theme_logo_base64(theme)
    if logo_b64:
        logo_html = f'<img class="logo-img" src="data:image/png;base64,{logo_b64}" alt="Known By Digital" />'
    else:
        logo_html = f'<div class="brand-logo-text">KNOWN BY <span>DIGITAL</span></div>'

    # Theme adaptive window colors
    if theme == "light":
        window_bg = "rgba(255, 255, 255, 0.96)"
        window_border = "rgba(226, 232, 240, 0.9)"
    elif theme == "orange":
        window_bg = "rgba(10, 10, 14, 0.92)"
        window_border = "rgba(255, 255, 255, 0.45)"
    else:
        window_bg = "rgba(18, 18, 22, 0.94)"
        window_border = "rgba(249, 115, 22, 0.35)"

    scenes_html = ""
    for idx, sc in enumerate(scenes_data):
        title = sc.get("title", "")
        words = title.split()
        if len(words) > 2:
            title_html = " ".join(words[:-1]) + f' <span>{words[-1]}</span>'
        else:
            title_html = f'<span>{title}</span>'

        subtitle = sc.get("subtitle", "")
        hud_chips = sc.get("hud_chips", [("Intake Speed", "4.2s"), ("Match Quality", "98.4%"), ("Conversion", "+42%")])
        hud_html = "".join([f"""
          <div class="hud-stat-chip">
            <div class="hud-stat-label">{label}</div>
            <div class="hud-stat-val">{val}</div>
          </div>
        """ for label, val in hud_chips])

        widget_type = sc.get("widget_type", "terminal")
        if widget_type == "terminal":
            widget_html = """
            <div class="ai-mascot-widget">
              <div class="mascot-stage">
                <div class="mascot-ring-glow"></div>
                <div class="mascot-hud-chip chip-left">⚡ 4s INTAKE</div>
                <div class="mascot-hud-chip chip-right">🤖 AUTOPILOT</div>
                <svg width="170" height="180" viewBox="0 0 200 210" fill="none" class="mascot-svg-anim" xmlns="http://www.w3.org/2000/svg">
                  <defs>
                    <linearGradient id="m-body" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stop-color="#1E293B" />
                      <stop offset="100%" stop-color="#0F172A" />
                    </linearGradient>
                    <linearGradient id="m-orange" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stop-color="#F97316" />
                      <stop offset="100%" stop-color="#EA580C" />
                    </linearGradient>
                    <filter id="m-glow" x="-20%" y="-20%" width="140%" height="140%">
                      <feGaussianBlur stdDeviation="8" result="blur" />
                      <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                  </defs>
                  <path d="M100 24 L100 42" stroke="#F97316" stroke-width="4" stroke-linecap="round"/>
                  <circle cx="100" cy="18" r="7" fill="#F97316" filter="url(#m-glow)" class="antenna-dot"/>
                  <rect x="42" y="42" width="116" height="86" rx="38" fill="url(#m-body)" stroke="#334155" stroke-width="3"/>
                  <rect x="56" y="58" width="88" height="46" rx="20" fill="#030712" stroke="#0EA5E9" stroke-width="2"/>
                  <circle cx="80" cy="81" r="9" fill="#00F0FF" filter="url(#m-glow)"/>
                  <circle cx="80" cy="81" r="3" fill="#FFFFFF"/>
                  <circle cx="120" cy="81" r="9" fill="#00F0FF" filter="url(#m-glow)"/>
                  <circle cx="120" cy="81" r="3" fill="#FFFFFF"/>
                  <rect x="32" y="68" width="10" height="28" rx="5" fill="#F97316"/>
                  <rect x="158" y="68" width="10" height="28" rx="5" fill="#F97316"/>
                  <ellipse cx="100" cy="136" rx="22" ry="6" fill="#1E293B" stroke="#475569" stroke-width="2"/>
                  <path d="M58 144 C58 144 75 140 100 140 C125 140 142 144 142 144 C150 152 154 175 148 200 C144 208 132 210 100 210 C68 210 56 208 52 200 C46 175 50 152 58 144 Z" fill="url(#m-body)" stroke="#334155" stroke-width="3"/>
                  <circle cx="100" cy="176" r="17" fill="#0F172A" stroke="#F97316" stroke-width="2.5"/>
                  <circle cx="100" cy="176" r="9" fill="url(#m-orange)" filter="url(#m-glow)" class="core-dot"/>
                  <path d="M100 168 L100 184 M92 176 L108 176" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="terminal-item" style="width: 100%; max-width: 680px;">
                <div class="terminal-icon">🤖</div>
                <div>
                  <div class="terminal-text-main">Autonomous Qualification Agent</div>
                  <div class="terminal-text-sub">Instant response • 4s intake • 0 Extra Headcount</div>
                </div>
                <div class="terminal-badge">LIVE 24/7</div>
              </div>
            </div>
            """
        elif widget_type == "comparison":
            widget_html = """
            <div class="comparison-widget">
              <div class="comp-col bad">
                <div class="comp-title bad">⚠️ Manual Workflow</div>
                <div class="comp-point">❌ 15m Response Delay</div>
                <div class="comp-point">❌ 60% Deal Bounce</div>
                <div class="comp-point">❌ Manual DM Chasing</div>
              </div>
              <div class="comp-col good">
                <div class="comp-title good">⚡ Autonomous Engine</div>
                <div class="comp-point">✅ 4s Instant Reply</div>
                <div class="comp-point">✅ 100% Leads Qualified</div>
                <div class="comp-point">✅ Auto Calendar Booking</div>
              </div>
            </div>
            """
        elif widget_type == "flowchart":
            widget_html = """
            <div class="flowchart-widget">
              <div class="flow-node">
                <div class="flow-icon">📥</div>
                <div>Omnichannel Lead Capture (Meta • IG • Web)</div>
              </div>
              <div class="flow-arrow">↓</div>
              <div class="flow-node active">
                <div class="flow-icon">🧠</div>
                <div>Gemini AI Agent (4s Intake & Filter)</div>
              </div>
              <div class="flow-arrow">↓</div>
              <div class="flow-node">
                <div class="flow-icon">📅</div>
                <div>Direct Calendar Booking & CRM Sync</div>
              </div>
            </div>
            """
        elif widget_type == "chart":
            widget_html = """
            <div class="chart-widget">
              <div class="chart-header">
                <div class="chart-tag">📈 30-Day Pipeline Velocity</div>
                <div style="font-size:13px; font-weight:800; color:#10B981; background:rgba(16,185,129,0.15); border:1px solid #10B981; padding:3px 10px; border-radius:999px;">+42% Growth</div>
              </div>
              <div class="chart-bars">
                <div class="bar-col">
                  <div class="bar-val">1.0x</div>
                  <div class="bar-fill" style="height: 25px;"></div>
                  <div class="bar-label">Wk 1</div>
                </div>
                <div class="bar-col">
                  <div class="bar-val">2.1x</div>
                  <div class="bar-fill" style="height: 50px;"></div>
                  <div class="bar-label">Wk 2</div>
                </div>
                <div class="bar-col">
                  <div class="bar-val">3.4x</div>
                  <div class="bar-fill" style="height: 78px;"></div>
                  <div class="bar-label">Wk 3</div>
                </div>
                <div class="bar-col">
                  <div class="bar-val">4.2x</div>
                  <div class="bar-fill" style="height: 105px; box-shadow: 0 0 25px rgba(249,115,22,0.6);"></div>
                  <div class="bar-label">Wk 4</div>
                </div>
              </div>
            </div>
            """
        elif widget_type == "cta":
            trigger = sc.get("trigger", "SYSTEM")
            widget_html = f"""
            <div class="cta-modal-widget">
              <div class="modal-badge">🎁 AGENCY GROWTH SOP</div>
              <div class="modal-title">MAKE YOUR BRAND AI-READY</div>
              <div class="modal-sub">Claim our private implementation architecture SOP</div>
              <div class="pulsing-cta-btn">COMMENT "{trigger}" BELOW ➔</div>
            </div>
            """
        else:
            widget_html = ""

        feat_tags = sc.get("feat_tags", ["✓ 0 Extra Headcount", "✓ 24/7 Live Agent", "✓ 100% CRM Sync"])
        tags_html = "".join([f'<div class="feat-tag">{tag}</div>' for tag in feat_tags])

        init_cls = "visible active" if idx == 0 else ""
        scenes_html += f"""
        <div class="scene-slide {init_cls}" id="scene-{idx}">
          <div class="hud-stats-bar">
            {hud_html}
          </div>

          <div class="text-block">
            <h1 class="hero-h1">{title_html}</h1>
            <p class="hero-p">{subtitle}</p>
          </div>

          <div class="widget-stage">
            {widget_html}
          </div>

          <div class="feature-tags-row">
            {tags_html}
          </div>
        </div>
        """

    return CANVA_REEL_ANIMATION_HTML.format(
        bg_color=t_cfg["bg_color"],
        text_color=t_cfg["text_color"],
        sub_color=t_cfg["sub_color"],
        window_bg=window_bg,
        window_border=window_border,
        logo_html=logo_html,
        scenes_html=scenes_html,
        total_duration=int(total_duration_seconds) + 1,
        total_duration_ms=int(total_duration_seconds * 1000)
    )

async def generate_viral_voiceover(script_text: str, output_path: str, voice: str = "en-US-GuyNeural") -> str:
    communicate = edge_tts.Communicate(script_text, voice=voice, rate="+8%")
    await communicate.save(output_path)
    return output_path

def mix_audio_with_ambient_bgm(voice_path: str, output_path: str, bgm_volume: float = 0.14) -> str:
    bgm_file = BASE_DIR / "assets" / "bgm_chill.mp3"
    if not bgm_file.exists():
        return voice_path

    cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(voice_path),
        "-i", str(bgm_file),
        "-filter_complex", f"[0:a]volume=1.0[v0];[1:a]volume={bgm_volume}[v1];[v0][v1]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "[aout]",
        "-c:a", "libmp3lame",
        "-q:a", "2",
        str(output_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        return str(output_path)
    return voice_path

def get_audio_duration_seconds(audio_path: str) -> float:
    cmd = [FFMPEG_BIN, "-i", str(audio_path)]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            return float(h)*3600 + float(m)*60 + float(s)
    return 12.0

def generate_canva_motion_reel(reel_data: dict, output_filename: str = "canva_reel.mp4", theme: str = None) -> str:
    if not theme:
        theme = get_current_day_theme()

    topic = reel_data.get("topic", "AI Automation for High-Growth Brands")
    hook = reel_data.get("hook_3s", "Stop Chasing Leads Manually")
    script = reel_data.get("voiceover_script", (
        "Stop losing seventy percent of high-intent deals to slow manual follow-ups. "
        "In 2026, top brands deploy autonomous AI agents that qualify and book in four seconds. "
        "Comment SYSTEM to get the architecture."
    ))
    trigger = reel_data.get("cta_trigger_word", "SYSTEM")

    # 1. Voiceover Audio + Copyright-Free Ambient BGM
    raw_voice = str(MEDIA_DIR / f"{Path(output_filename).stem}_voice_raw.mp3")
    asyncio.run(generate_viral_voiceover(script, raw_voice, voice="en-US-GuyNeural"))

    mixed_audio = str(MEDIA_DIR / f"{Path(output_filename).stem}_voice_mixed.mp3")
    final_audio = mix_audio_with_ambient_bgm(raw_voice, mixed_audio, bgm_volume=0.14)
    duration = get_audio_duration_seconds(final_audio)

    # STRICT 7 TO 15 SECONDS ENFORCEMENT
    if duration > 15.0:
        speed_factor = min(2.0, duration / 14.0)
        fast_audio = str(MEDIA_DIR / f"{Path(output_filename).stem}_voice_fast.mp3")
        subprocess.run([
            FFMPEG_BIN, "-y",
            "-i", str(final_audio),
            "-filter:a", f"atempo={speed_factor:.2f}",
            "-c:a", "libmp3lame",
            "-q:a", "2",
            fast_audio
        ], check=True)
        final_audio = fast_audio
        duration = get_audio_duration_seconds(final_audio)
        print(f"[Canva Motion Engine] Adjusted Reel audio to {duration:.1f}s to strictly stay within 7-15s.")
    elif duration < 7.0:
        duration = 7.5

    # 2. Build Structured Scenes for Canva Motion Graphic Flow
    scenes = [
        {
            "widget_type": "terminal",
            "hud_chips": [("Intake Speed", "4.2s"), ("Match Quality", "98.4%"), ("Conversion", "+42%")],
            "title": hook,
            "subtitle": "High-growth founders don't hire more reps. They deploy autonomous intake engines that qualify in 4s.",
            "feat_tags": ["✓ 0 Extra Headcount", "✓ 24/7 Live Agent", "✓ 100% CRM Sync"]
        },
        {
            "widget_type": "comparison",
            "hud_chips": [("Response Lag", "15m"), ("Deal Bounce", "60%"), ("Revenue Loss", "HIGH")],
            "title": "Every 10-Minute Delay Bleeds 60% of Deals",
            "subtitle": "When human follow-up lags, ready-to-buy clients bounce straight to your fastest competitor.",
            "feat_tags": ["⚠️ 60% Deal Dropoff", "⚠️ Slow Follow-Up Kills ROI", "⚠️ Zero 24/7 Coverage"]
        },
        {
            "widget_type": "flowchart",
            "hud_chips": [("Capture Speed", "Instant"), ("AI Filter", "4s"), ("Calendar Sync", "100%")],
            "title": "Deploy An Autonomous Revenue Loop",
            "subtitle": "Filter out time-wasters, capture high-ticket intent, and book qualified calls on autopilot.",
            "feat_tags": ["✓ 4-Second Response", "✓ Native CRM Sync", "✓ Zero Hallucinations"]
        },
        {
            "widget_type": "chart",
            "hud_chips": [("Pipeline Speed", "4.2x"), ("Lead Volume", "+42%"), ("CAC Reduction", "-65%")],
            "title": "Scale Your Output, Not Payroll",
            "subtitle": "Automate 80% of repetitive operational tasks while your team focuses on closing.",
            "feat_tags": ["✓ 4.2x Velocity", "✓ +42% Inbound Leads", "✓ 99.9% System Uptime"]
        },
        {
            "widget_type": "cta",
            "trigger": trigger,
            "hud_chips": [("Setup Window", "24h"), ("Headcount Needed", "0"), ("System Uptime", "99.9%")],
            "title": "Want This System Built For You?",
            "subtitle": f"Comment '{trigger}' below or DM @knownbydigital to claim your custom growth roadmap.",
            "feat_tags": ["✓ Free Agency Blueprint", "✓ Tailored to Your Stack", "✓ Limited Spots"]
        }
    ]

    # 3. Render and Record Canva Motion Video in Real-Time with Playwright
    html_content = generate_canva_reel_html(scenes, duration, theme=theme)
    
    # Use unique folder per run so no stale WebM files are ever read
    rec_id = int(time.time() * 1000)
    temp_video_dir = MEDIA_DIR / f"temp_rec_{rec_id}"
    temp_video_dir.mkdir(exist_ok=True, parents=True)

    # 3. Generate Dedicated High-Converting Single-Post-Quality Cover Thumbnail
    cover_image_path = str(MEDIA_DIR / f"{Path(output_filename).stem}_cover.jpg")
    generate_pro_reel_cover_image(reel_data, output_filename=Path(cover_image_path).name, theme=theme)
    print(f"[Canva Motion Engine] Dedicated Single-Post-Quality Reel cover generated: {cover_image_path}")

    # 4. Render and Record Canva Motion Video in Real-Time with Playwright
    print(f"[Canva Motion Engine] Recording {duration:.1f}s 60FPS dynamic animation in Chromium (1080x1920)...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # CRITICAL: Both viewport and record_video_size MUST match 1080x1920 to eliminate grey bars!
        context = browser.new_context(
            viewport={"width": 1080, "height": 1920},
            record_video_dir=str(temp_video_dir),
            record_video_size={"width": 1080, "height": 1920},
            device_scale_factor=1
        )
        page = context.new_page()
        page.set_viewport_size({"width": 1080, "height": 1920})
        page.set_content(html_content, wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        # Wait for the exact audio duration
        page.wait_for_timeout(int(duration * 1000) + 800)
        context.close()
        browser.close()

    # Find the recorded WebM file
    webm_files = list(temp_video_dir.glob("*.webm"))
    if not webm_files:
        raise RuntimeError("No recorded video found from Playwright Chromium.")
    recorded_webm = webm_files[0]

    # 4. Merge Recorded Animated Video with Voiceover & Ambient BGM using FFmpeg
    output_video_path = str(MEDIA_DIR / output_filename)
    merge_cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(recorded_webm),
        "-i", str(final_audio),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_video_path)
    ]
    print(f"[Canva Motion Engine] Merging audio and video into {output_video_path}...")
    subprocess.run(merge_cmd, check=True)

    # Cleanup temp video dir
    try:
        recorded_webm.unlink()
        temp_video_dir.rmdir()
    except Exception:
        pass

    print(f"[Canva Motion Engine] Done! Created: {output_video_path} (Cover: {cover_image_path})")
    return output_video_path, cover_image_path

if __name__ == "__main__":
    v, c = generate_canva_motion_reel({}, "test_canva_perfect.mp4", theme="dark")
    print("Created:", v, c)
