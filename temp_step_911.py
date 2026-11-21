& "C:\Users\Nion\AppData\Local\Programs\Python\Python312\python.exe" -c "
from playwright.sync_api import sync_playwright

html = '''<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800;900&family=Inter:wght@500;600;700;800&display=swap');
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    width: 1080px; height: 1920px;
    background-color: #08080A;
    background-image: 
      radial-gradient(circle at 50% 10%, rgba(249, 115, 22, 0.22) 0%, transparent 60%),
      radial-gradient(circle at 50% 90%, rgba(234, 88, 12, 0.18) 0%, transparent 60%),
      radial-gradient(rgba(249, 115, 22, 0.16) 1.5px, transparent 1.5px);
    background-size: auto, auto, 36px 36px;
    color: #FFFFFF;
    font-family: 'Plus Jakarta Sans', sans-serif;
    display: flex; flex-direction: column; align-items: center; justify-content: space-between;
    padding: 90px 65px 85px 65px;
    overflow: hidden;
  }
  .top-progress { position: absolute; top: 0; left: 0; width: 100%; height: 12px; background: rgba(255,255,255,0.1); }
  .top-progress-fill { width: 50%; height: 100%; background: linear-gradient(90deg, #F97316, #FB923C); box-shadow: 0 0 20px #F97316; }

  /* Brand Header */
  .header-brand { display: flex; align-items: center; justify-content: space-between; width: 100%; max-width: 950px; margin-bottom: 24px; }
  .brand-logo-text { font-size: 28px; font-weight: 900; letter-spacing: 2.5px; }
  .brand-logo-text span { color: #F97316; }
  .hud-badge { background: rgba(249, 115, 22, 0.15); border: 1.5px solid rgba(249, 115, 22, 0.4); padding: 9px 24px; border-radius: 999px; font-size: 16px; font-weight: 800; color: #F97316; letter-spacing: 2px; }

  /* Tech SaaS Window Frame */
  .tech-window {
    width: 100%; max-width: 950px; height: 1560px;
    background: rgba(18, 18, 22, 0.94);
    border: 2px solid rgba(249, 115, 22, 0.35);
    border-radius: 40px;
    box-shadow: 0 35px 80px rgba(0, 0, 0, 0.8), 0 0 50px rgba(249, 115, 22, 0.18);
    backdrop-filter: blur(30px);
    display: flex; flex-direction: column; justify-content: space-between;
    overflow: hidden;
  }
  .window-titlebar {
    height: 75px; background: rgba(255, 255, 255, 0.03);
    border-bottom: 1.5px solid rgba(255, 255, 255, 0.08);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 32px;
  }
  .window-dots { display: flex; gap: 11px; }
  .dot { width: 15px; height: 15px; border-radius: 50%; }
  .dot-red { background: #EF4444; }
  .dot-yellow { background: #F59E0B; }
  .dot-green { background: #10B981; }
  .window-url {
    background: rgba(0, 0, 0, 0.45); border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 999px; padding: 7px 26px; font-size: 16px; font-family: 'Inter', sans-serif;
    color: #A3A3A3; letter-spacing: 1px;
  }
  .window-url span { color: #F97316; font-weight: 700; }
  .window-status { display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 800; color: #10B981; letter-spacing: 1.5px; }
  .status-pulse { width: 11px; height: 11px; border-radius: 50%; background: #10B981; box-shadow: 0 0 12px #10B981; }

  /* Body Content */
  .window-body {
    flex: 1; padding: 50px 48px; display: flex; flex-direction: column;
    align-items: center; justify-content: space-between; text-align: center;
  }

  /* 1. HUD Stats Bar */
  .hud-stats-bar {
    width: 100%; display: flex; justify-content: space-between; gap: 14px;
  }
  .hud-stat-chip {
    flex: 1; background: rgba(255, 255, 255, 0.04); border: 1.5px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px; padding: 14px 18px; text-align: center;
  }
  .hud-stat-label { font-size: 13px; font-family: 'Inter', sans-serif; color: #A3A3A3; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 4px; }
  .hud-stat-val { font-size: 26px; font-weight: 900; color: #F97316; }

  /* 2. Visual Terminal UI Widget (Rich Inbound Feed Illustration) */
  .terminal-widget {
    width: 100%; background: rgba(0, 0, 0, 0.45);
    border: 1.5px solid rgba(249, 115, 22, 0.3); border-radius: 28px;
    padding: 28px 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    display: flex; flex-direction: column; gap: 16px; text-align: left;
    margin: 20px 0;
  }
  .terminal-header {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }
  .terminal-tag { font-size: 14px; font-weight: 800; letter-spacing: 2px; color: #F97316; text-transform: uppercase; }
  .terminal-time { font-size: 13px; font-family: 'Inter', sans-serif; color: #737373; font-weight: 600; }
  .terminal-item {
    display: flex; align-items: center; gap: 18px; background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 18px; padding: 16px 20px;
  }
  .terminal-icon {
    width: 44px; height: 44px; border-radius: 12px;
    background: rgba(249, 115, 22, 0.15); border: 1px solid #F97316;
    display: flex; align-items: center; justify-content: center; font-size: 22px; flex-shrink: 0;
  }
  .terminal-text-main { font-size: 19px; font-weight: 800; color: #FFF; margin-bottom: 2px; }
  .terminal-text-sub { font-size: 14px; color: #A3A3A3; font-weight: 500; font-family: 'Inter', sans-serif; }
  .terminal-badge {
    margin-left: auto; background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981;
    color: #10B981; padding: 6px 16px; border-radius: 999px; font-size: 14px; font-weight: 800;
  }

  /* 3. Headlines */
  .text-block { width: 100%; margin: 10px 0 25px 0; }
  .hero-h1 { font-size: 60px; font-weight: 900; line-height: 1.18; letter-spacing: -2px; margin-bottom: 16px; }
  .hero-h1 span { color: #F97316; }
  .hero-p { font-size: 24px; color: #A3A3A3; line-height: 1.5; max-width: 820px; font-weight: 500; margin: auto; }

  /* 4. Bottom Feature Badges */
  .feature-tags-row {
    display: flex; gap: 14px; justify-content: center; width: 100%; flex-wrap: wrap;
  }
  .feat-tag {
    background: rgba(249, 115, 22, 0.12); border: 1.5px solid rgba(249, 115, 22, 0.35);
    color: #F97316; font-size: 18px; font-weight: 800; padding: 12px 28px; border-radius: 999px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  }

  /* Footer */
  .window-footer {
    height: 65px; background: rgba(0, 0, 0, 0.45);
    border-top: 1.5px solid rgba(255, 255, 255, 0.08);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 700;
    letter-spacing: 2px; color: #737373;
  }
  .window-footer span { color: #F97316; }
</style>
</head>
<body>
  <div class='top-progress'><div class='top-progress-fill'></div></div>
  <div class='header-brand'>
    <div class='brand-logo-text'>KNOWN BY <span>DIGITAL</span></div>
    <div class='hud-badge'>⚡ 2026 ARCHITECTURE</div>
  </div>
  <div class='tech-window'>
    <div class='window-titlebar'>
      <div class='window-dots'>
        <div class='dot dot-red'></div>
        <div class='dot dot-yellow'></div>
        <div class='dot dot-green'></div>
      </div>
      <div class='window-url'>app.knownbydigital.com/<span>revenue-engine</span></div>
      <div class='window-status'>
        <div class='status-pulse'></div> LIVE 24/7
      </div>
    </div>
    <div class='window-body'>
      <div class='hud-stats-bar'>
        <div class='hud-stat-chip'>
          <div class='hud-stat-label'>Intake Speed</div>
          <div class='hud-stat-val'>4.2s</div>
        </div>
        <div class='hud-stat-chip'>
          <div class='hud-stat-label'>Match Quality</div>
          <div class='hud-stat-val'>98.4%</div>
        </div>
        <div class='hud-stat-chip'>
          <div class='hud-stat-label'>Conversion</div>
          <div class='hud-stat-val'>+42%</div>
        </div>
      </div>

      <div class='terminal-widget'>
        <div class='terminal-header'>
          <div class='terminal-tag'>⚡ Live Inbound Stream</div>
          <div class='terminal-time'>Updated 2s ago</div>
        </div>
        <div class='terminal-item'>
          <div class='terminal-icon'>🛒</div>
          <div>
            <div class='terminal-text-main'>Shopify Plus Enterprise Store</div>
            <div class='terminal-text-sub'>High-Intent Inquiry • Deal Value: $12,500</div>
          </div>
          <div class='terminal-badge'>QUALIFIED</div>
        </div>
        <div class='terminal-item'>
          <div class='terminal-icon'>📅</div>
          <div>
            <div class='terminal-text-main'>Autonomous Calendar Slot Confirmed</div>
            <div class='terminal-text-sub'>Instant CRM Sync • Zero Manual Lag</div>
          </div>
          <div class='terminal-badge'>BOOKED</div>
        </div>
      </div>

      <div class='text-block'>
        <h1 class='hero-h1'>Stop Chasing Leads. <span>Automate.</span></h1>
        <p class='hero-p'>High-growth founders don't hire more reps. They deploy autonomous intake engines that qualify and book in 4 seconds.</p>
      </div>

      <div class='feature-tags-row'>
        <div class='feat-tag'>✓ 0 Extra Headcount</div>
        <div class='feat-tag'>✓ 24/7 Live Agent</div>
        <div class='feat-tag'>✓ 100% CRM Sync</div>
      </div>
    </div>
    <div class='window-footer'>
      KNOWN BY DIGITAL SYSTEM • <span>99.9% UPTIME</span> • ENCRYPTED 256-BIT
    </div>
  </div>
</body>
</html>'''

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1080, 'height': 1920})
    page.set_content(html)
    page.screenshot(path='generated_media/ui_perfect_filled.png')
    browser.close()
print('Full UI Frame rendered!')
"