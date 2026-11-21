from playwright.sync_api import sync_playwright
from canva_reel_engine import generate_canva_reel_html

scenes = [
    {
        'widget_type': 'terminal',
        'hud_chips': [('Intake Speed', '4.2s'), ('Match Quality', '98.4%'), ('Conversion', '+42%')],
        'title': 'Stop Losing 70% of Sales',
        'subtitle': 'High-growth founders deploy autonomous intake engines that qualify and book in 4 seconds.',
        'feat_tags': ['✓ 0 Extra Headcount', '✓ 24/7 Live Agent', '✓ 100% CRM Sync']
    }
]

html = generate_canva_reel_html(scenes, 10.0, theme='dark')
html = html.replace('id="scene-0">', 'class="scene-slide visible active" id="scene-0">')

cover_path = 'generated_media/test_standalone_cover.jpg'
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1080, 'height': 1920})
    page.set_content(html, wait_until='networkidle')
    page.evaluate('document.fonts.ready')
    page.screenshot(path=cover_path, type='jpeg', quality=95)
    browser.close()

print('Standalone cover rendered at:', cover_path)
