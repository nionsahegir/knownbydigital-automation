import os
import sys
from pathlib import Path
from canva_reel_engine import generate_canva_motion_reel

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def generate_faceless_reel(reel_data: dict, output_filename: str = "kbd_reel.mp4", theme: str = "dark"):
    """Generates continuous Canva-style animated motion graphic Reel in high-converting Stealth Dark SaaS mode with dedicated cover thumbnail."""
    # Dark mode provides maximum visual contrast for Instagram's 9:16 vertical player
    return generate_canva_motion_reel(reel_data, output_filename=output_filename, theme="dark")

if __name__ == "__main__":
    print("Testing reel generator bridge...")
    v, c = generate_faceless_reel({}, "bridge_test.mp4")
    print("Bridge created:", v, "Cover:", c)
