import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
THEME_STATE_FILE = BASE_DIR / "theme_state.json"

THEME_ORDER = ["dark", "orange", "light"]

THEME_DISPLAY_NAMES = {
    "dark": "Stealth Charcoal (Black BG, White & Orange Text)",
    "orange": "High-Impact Orange (Orange BG, White & Black Text)",
    "light": "Clean Editorial (White BG, Orange & Charcoal Text)"
}

def load_theme_state() -> dict:
    if THEME_STATE_FILE.exists():
        try:
            with open(THEME_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"current_theme": "dark", "last_date": "", "history": []}

def save_theme_state(state: dict):
    with open(THEME_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def get_today_theme(force_advance: bool = False) -> str:
    """
    Returns the theme for today.
    Rotates in strict sequence: dark -> orange -> light -> dark.
    Guarantees all 4 posts in a single day share the exact same theme.
    Uses calendar date anchor so rotation continues seamlessly even across
    ephemeral runners or stateless cloud containers.
    """
    from datetime import date
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")

    # If force_advance is requested, use state file
    if force_advance:
        state = load_theme_state()
        last_theme = state.get("current_theme", "dark")
        try:
            curr_idx = THEME_ORDER.index(last_theme)
            next_theme = THEME_ORDER[(curr_idx + 1) % len(THEME_ORDER)]
        except ValueError:
            next_theme = "orange"
        state["current_theme"] = next_theme
        state["last_date"] = today_str
        save_theme_state(state)
        return next_theme

    # Anchor date: 2026-11-01 starts Stealth Charcoal (0 = "dark")
    anchor_date = date(2026, 11, 1)
    delta_days = (today - anchor_date).days
    theme_idx = delta_days % len(THEME_ORDER)
    current_theme = THEME_ORDER[theme_idx]

    try:
        state = load_theme_state()
        state["current_theme"] = current_theme
        state["last_date"] = today_str
        save_theme_state(state)
    except Exception:
        pass

    print(f"[Theme Manager] Active Theme for {today_str}: {current_theme} ({THEME_DISPLAY_NAMES.get(current_theme)})")
    return current_theme

def set_current_theme(theme_name: str) -> str:
    """Manually override current theme."""
    if theme_name not in THEME_ORDER:
        raise ValueError(f"Invalid theme: {theme_name}. Choose from {THEME_ORDER}")
    today_str = datetime.now().strftime("%Y-%m-%d")
    state = load_theme_state()
    state["current_theme"] = theme_name
    state["last_date"] = today_str
    save_theme_state(state)
    print(f"[Theme Manager] Theme set manually to: {theme_name}")
    return theme_name

# Universal alias
get_current_day_theme = get_today_theme

if __name__ == "__main__":
    t = get_today_theme()
    print("Today's Theme:", t)
