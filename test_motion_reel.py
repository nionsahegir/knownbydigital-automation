import os
import sys
import asyncio
import subprocess
from pathlib import Path
import imageio_ffmpeg
from playwright.sync_api import sync_playwright
import edge_tts
from html_renderer import THEME_CONFIGS, get_theme_logo_base64

FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
BASE_DIR = Path(__file__).resolve().parent
MEDIA_DIR = BASE_DIR / "generated_media"
MEDIA_DIR.mkdir(exist_ok=True)

# Minimalist, punchy, motion-graphic HTML template for Reel scenes
MOTION_REEL_SCENE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800;900&family=Inter:wght@600;700;800&display=swap');
  
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
    font-family: 'Plus Jakarta Sans', sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
    padding: 140px 90px;
    overflow: hidden;
    position: relative;
    text-align: center;
  }}

  /* Top Section - Logo Only (NO page numbers or slide counters) */
  .top-section {{
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    z-index: 10;
  }}

  .logo-img {{
    height: 70px;
    width: auto;
    object-fit: contain;
  }}

  /* Main Kinetic Body */
  .center-container {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    max-width: 960px;
    z-index: 10;
    margin: 50px 0;
  }}

  .badge-pill {{
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-family: 'Inter', sans-serif;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: {accent_color};
    background: {card_bg};
    border: 1.5px solid {card_border};
    padding: 14px 34px;
    border-radius: 999px;
    margin-bottom: 40px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }}

  /* Large Motion Graphic Visual Centerpiece */
  .visual-diamond {{
    width: 380px;
    height: 380px;
    background: linear-gradient(135deg, {accent_color} 0%, #EA580C 100%);
    border-radius: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 20px 60px rgba(249, 115, 22, 0.35);
    margin-bottom: 50px;
    position: relative;
  }}

  .visual-inner {{
    width: 320px;
    height: 320px;
    background: {bg_color};
    border-radius: 45px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 25px;
  }}

  .visual-icon {{
    font-size: 90px;
    margin-bottom: 10px;
  }}

  .visual-stat {{
    font-size: 56px;
    font-weight: 900;
    color: {accent_color};
    line-height: 1;
  }}

  .visual-stat-label {{
    font-family: 'Inter', sans-serif;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 2px;
    color: {sub_color};
    text-transform: uppercase;
    margin-top: 8px;
  }}

  /* High Impact Bold Headline */
  .bold-headline {{
    font-size: 74px;
    font-weight: 900;
    line-height: 1.15;
    letter-spacing: -2px;
    color: {text_color};
    max-width: 920px;
    margin-bottom: 30px;
  }}

  .bold-headline .highlight {{
    color: {accent_color};
    background: linear-gradient(135deg, #F97316 0%, #FB923C 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}

  .sub-headline {{
    font-family: 'Inter', sans-serif;
    font-size: 30px;
    font-weight: 600;
    color: {sub_color};
    line-height: 1.45;
    max-width: 860px;
  }}

  /* High Converting CTA Button */
  .cta-pill {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: {btn_bg};
    color: {btn_color};
    font-size: 28px;
    font-weight: 900;
    letter-spacing: 2px;
    padding: 26px 65px;
    border-radius: 999px;
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.25);
    margin-top: 40px;
    text-transform: uppercase;
  }}

  /* Footer */
  .footer-section {{
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    z-index: 10;
  }}

  .footer-handle {{
    font-family: 'Inter', sans-serif;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 1px;
    color: {sub_color};
  }}

  .footer-handle span {{
    color: {accent_color};
  }}
</style>
</head>
<body>
  <!-- Clean Centered Brand Header -->
  <div class="top-section">
    {logo_html}
  </div>

  <!-- Center Content -->
  <div class="center-container">
    {content_html}
  </div>

  <!-- Clean Minimalist Footer -->
  <div class="footer-section">
    <div class="footer-handle">@knownbydigital • <span>knownbydigital.com</span></div>
  </div>
</body>
</html>
"""

def render_motion_scene_html(scene: dict, theme: str = "dark") -> str:
    t_cfg = THEME_CONFIGS.get(theme, THEME_CONFIGS["dark"])
    logo_b64 = get_theme_logo_base64(theme)
    if logo_b64:
        logo_html = f'<img class="logo-img" src="data:image/png;base64,{logo_b64}" alt="Known By Digital" />'
    else:
        logo_html = f'<div style="font-weight:900; font-size:26px; letter-spacing:2px; color:{t_cfg["text_color"]};">KNOWN BY <span style="color:{t_cfg["accent_color"]};">DIGITAL</span></div>'

    title = scene.get("title", "")
    words = title.split()
    if len(words) > 2:
        title_html = " ".join(words[:-1]) + f' <span class="highlight">{words[-1]}</span>'
    else:
        title_html = f'<span class="highlight">{title}</span>'

    badge = scene.get("badge", "SYSTEM")
    subtitle = scene.get("subtitle", "")
    icon = scene.get("icon", "⚡")
    stat = scene.get("stat", "")
    stat_label = scene.get("stat_label", "")
    is_cta = scene.get("is_cta", False)

    visual_block = ""
    if stat:
        visual_block = f"""
        <div class="visual-diamond">
          <div class="visual-inner">
            <div class="visual-stat">{stat}</div>
            <div class="visual-stat-label">{stat_label}</div>
          </div>
        </div>
        """
    elif icon:
        visual_block = f"""
        <div class="visual-diamond">
          <div class="visual-inner">
            <div class="visual-icon">{icon}</div>
          </div>
        </div>
        """

    cta_btn = ""
    if is_cta:
        trigger = scene.get("trigger", "SYSTEM")
        cta_btn = f'<div class="cta-pill">COMMENT "{trigger}" BELOW ➔</div>'

    content_html = f"""
    <div class="badge-pill">{badge}</div>
    {visual_block}
    <h1 class="bold-headline">{title_html}</h1>
    <p class="sub-headline">{subtitle}</p>
    {cta_btn}
    """

    return MOTION_REEL_SCENE_TEMPLATE.format(
        bg_color=t_cfg["bg_color"],
        bg_gradient=t_cfg["bg_gradient"],
        text_color=t_cfg["text_color"],
        sub_color=t_cfg["sub_color"],
        accent_color=t_cfg["accent_color"],
        card_bg=t_cfg["card_bg"],
        card_border=t_cfg["card_border"],
        btn_bg=t_cfg["btn_bg"],
        btn_color=t_cfg["btn_color"],
        logo_html=logo_html,
        content_html=content_html
    )

async def generate_viral_voiceover(script_text: str, output_path: str, voice: str = "en-US-GuyNeural") -> str:
    """Uses energetic, natural American voice (en-US-GuyNeural) with natural conversational pacing."""
    communicate = edge_tts.Communicate(script_text, voice=voice, rate="+2%")
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

def build_smooth_transition_reel(image_paths: list, audio_path: str, output_video_path: str) -> str:
    """
    Renders video with smooth crossfade / slide transitions using FFmpeg xfade
    instead of abrupt static cuts.
    """
    # 1. Get audio duration
    cmd = [FFMPEG_BIN, "-i", str(audio_path)]
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    duration = 20.0
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            duration = float(h)*3600 + float(m)*60 + float(s)
            break

    n = len(image_paths)
    per_scene = duration / n
    trans_dur = 0.5  # 0.5s smooth transition

    print(f"[Smooth Motion Builder] {n} scenes, ~{per_scene:.1f}s each, audio duration: {duration:.1f}s")

    # Build FFmpeg command with xfade filters
    # Convert each image to a video segment of length per_scene + trans_dur
    input_args = []
    filter_chains = []

    for i, p in enumerate(image_paths):
        # loop image for per_scene + trans_dur
        seg_dur = per_scene + (trans_dur if i < n - 1 else 0.2)
        input_args.extend(["-loop", "1", "-t", f"{seg_dur:.2f}", "-i", Path(p).as_posix()])

    # Build xfade graph
    # [0][1] xfade=transition=fade:duration=0.5:offset=(per_scene - 0.5) [v1]
    # [v1][2] xfade=transition=fade:duration=0.5:offset=(2*per_scene - 1.0) [v2] ...
    last_v = "0:v"
    current_offset = per_scene - trans_dur

    for i in range(1, n):
        out_v = f"v{i}"
        filter_chains.append(
            f"[{last_v}][{i}:v]xfade=transition=fade:duration={trans_dur}:offset={current_offset:.2f}[{out_v}]"
        )
        last_v = out_v
        current_offset += (per_scene - trans_dur)

    filter_str = ";".join(filter_chains)
    filter_str += f";[{last_v}]format=yuv420p[final_v]"

    full_cmd = [
        FFMPEG_BIN, "-y",
        *input_args,
        "-i", str(audio_path),
        "-filter_complex", filter_str,
        "-map", "[final_v]",
        "-map", f"{n}:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-r", "30",
        str(output_video_path)
    ]

    print("[Smooth Motion Builder] Encoding reel with crossfade transitions...")
    run_res = subprocess.run(full_cmd, capture_output=True, text=True, errors="replace")
    if run_res.returncode != 0:
        print("[Fallback to Concat] xfade error:", run_res.stderr[-400:])
        # Fallback to standard concat if complex filter has offset discrepancy
        concat_file = MEDIA_DIR / "temp_concat.txt"
        with open(concat_file, "w") as f:
            for p in image_paths:
                f.write(f"file '{Path(p).as_posix()}'\n")
                f.write(f"duration {per_scene:.2f}\n")
            f.write(f"file '{Path(image_paths[-1]).as_posix()}'\n")
        cmd_fallback = [
            FFMPEG_BIN, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-i", str(audio_path),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k", "-shortest", "-r", "30",
            str(output_video_path)
        ]
        subprocess.run(cmd_fallback, check=True)
        if concat_file.exists(): concat_file.unlink()

    print(f"[Smooth Motion Builder] Done! Created: {output_video_path}")
    return str(output_video_path)

def generate_pro_motion_reel(reel_data: dict, output_filename: str = "motion_reel.mp4", theme: str = "dark") -> str:
    # 1. High Energy, Conversational Voiceover Script
    script = (
        "Be honest — are you still wasting hours manually qualifying inbound leads? "
        "Here's the brutal truth: every ten-minute response delay drops your sales conversion by sixty percent. "
        "High-growth brands aren't hiring more reps — they're deploying autonomous AI engines. "
        "Instant multi-touch qualification, real-time CRM updates, and zero extra headcount. "
        "Comment SYSTEM below, and we'll send you our complete private agency blueprint."
    )

    raw_voice = str(MEDIA_DIR / "motion_voice_raw.mp3")
    asyncio.run(generate_viral_voiceover(script, raw_voice, voice="en-US-GuyNeural"))

    mixed_audio = str(MEDIA_DIR / "motion_voice_mixed.mp3")
    final_audio = mix_audio_with_ambient_bgm(raw_voice, mixed_audio, bgm_volume=0.14)

    # 2. Modern 5-Scene Kinetic Flow (NO page numbers, NO slide counters)
    scenes = [
        {
            "badge": "⚡ HONEST QUESTION",
            "icon": "⏳",
            "title": "Still Chasing Leads Manually?",
            "subtitle": "Most founders lose 60% of high-intent clients before their first call."
        },
        {
            "badge": "⚠️ THE PROFIT LEAK",
            "stat": "-60%",
            "stat_label": "Conversion Drop",
            "title": "Every 10-Minute Delay Kills The Deal",
            "subtitle": "Human follow-up lag is silently bleeding your ad ROI."
        },
        {
            "badge": "🚀 THE AI SOLUTION",
            "icon": "🤖",
            "title": "Deploy An Autonomous Revenue Engine",
            "subtitle": "Instant intent capture across Meta & Web in under 4 seconds."
        },
        {
            "badge": "📈 VERIFIED CLIENT IMPACT",
            "stat": "4.2x",
            "stat_label": "ROAS Scaling",
            "title": "Zero Extra Headcount Needed",
            "subtitle": "Automate 80% of repetitive workflows while your team sleeps."
        },
        {
            "badge": "🎁 FREE AGENCY SOP",
            "icon": "📥",
            "title": "Want This System Built For You?",
            "subtitle": "Comment 'SYSTEM' below to claim our complete implementation guide.",
            "is_cta": True,
            "trigger": "SYSTEM"
        }
    ]

    # 3. Render High-Res HTML Scenes
    image_paths = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        for idx, sc in enumerate(scenes):
            html = render_motion_scene_html(sc, theme=theme)
            out_img = str(MEDIA_DIR / f"motion_scene_{idx+1}.png")
            page.set_content(html, wait_until="networkidle")
            page.screenshot(path=out_img)
            image_paths.append(out_img)
        browser.close()

    # 4. Render Video with Smooth Motion Transitions
    out_video = str(MEDIA_DIR / output_filename)
    build_smooth_transition_reel(image_paths, final_audio, out_video)
    return out_video

if __name__ == "__main__":
    print("Testing Pro Motion Reel Generation...")
    v = generate_pro_motion_reel({}, "pro_motion_reel_test.mp4", theme="dark")
    print("Result:", v)
