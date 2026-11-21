import json
import os
import sys
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
TOPIC_HISTORY_FILE = BASE_DIR / "topic_history.json"

CONTENT_PILLARS = [
    {
        "id": "ai_automation",
        "name": "AI Automation & Autonomous Intake Engines",
        "focus": "4-second lead qualification, 24/7 autonomous agents, CRM synchronization, zero extra headcount.",
        "services_mentioned": ["Custom AI Agent Development", "Autonomous Lead Intake Engines", "CRM Workflow Automation"]
    },
    {
        "id": "website_building",
        "name": "High-Converting Website Building & Modern Web Development",
        "focus": "Next.js / Shopify Plus / Headless web design, lightning-fast load times, landing page conversion rate optimization (CRO), modern UI/UX that turns visitors into high-ticket clients.",
        "services_mentioned": ["Custom Website Design & Development", "Shopify Store Re-platforming", "High-Converting B2B Landing Pages"]
    },
    {
        "id": "agency_operations",
        "name": "Agency Operations & Revenue Systems",
        "focus": "Cutting operational overhead by 40%, eliminating manual follow-up delays, automated client onboarding, scalable tech stacks.",
        "services_mentioned": ["Operations Architecture Consulting", "Full-Stack Automation Audits", "Custom Dashboard Integration"]
    },
    {
        "id": "service_showcase_offers",
        "name": "Direct Service Showcases & Limited-Time VIP Offers",
        "focus": "Directly showcasing Known By Digital's agency services ('We build your AI-ready website and automated pipeline'), offering Free 1-on-1 Growth Audits, and exclusive VIP implementation slots.",
        "services_mentioned": ["Full Agency Done-For-You Implementation", "Free 1-on-1 Architecture Audit", "VIP Growth Blueprint Roadmap"]
    }
]

def load_topic_history() -> list:
    if not TOPIC_HISTORY_FILE.exists():
        return []
    try:
        with open(TOPIC_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def get_recent_topics(limit: int = 35) -> list:
    history = load_topic_history()
    recent = history[-limit:] if len(history) > limit else history
    topics = []
    for item in recent:
        if isinstance(item, dict):
            for fmt in ["reel", "single_post", "carousel", "story"]:
                val = item.get(fmt)
                if val and isinstance(val, str):
                    topics.append(val)
                elif val and isinstance(val, dict):
                    topics.append(val.get("topic", val.get("headline", val.get("hook_3s", ""))))
    return [t for t in topics if t]

def record_published_pack(pack: dict):
    history = load_topic_history()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "reel": pack.get("reel", {}).get("hook_3s", pack.get("reel", {}).get("topic", "")),
        "single_post": pack.get("single_post", {}).get("headline", ""),
        "carousel": pack.get("carousel", {}).get("topic", pack.get("carousel", {}).get("headline", "")),
        "story": pack.get("story", {}).get("headline", "Growth Poll & Reel Spotlight")
    }
    history.append(entry)
    with open(TOPIC_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print(f"[Topic Memory] Recorded {entry['date']} topics to memory. Total history: {len(history)} entries.")

def get_current_pillar() -> dict:
    """Rotates across the 4 strategic pillars based on day of year."""
    day_num = datetime.now().timetuple().tm_yday
    return CONTENT_PILLARS[day_num % len(CONTENT_PILLARS)]

if __name__ == "__main__":
    pillar = get_current_pillar()
    print("Today's Strategic Pillar:", pillar["name"])
    print("Recent topics:", len(get_recent_topics()))
