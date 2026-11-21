import json
import os
import sys
from datetime import datetime
from config import GEMINI_API_KEY, BRAND
from google import genai
from google.genai import types

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SYSTEM_PROMPT = f"""
You are the Chief Content Strategist & Organic Social SEO Architect for '{BRAND['name']}' ({BRAND['website']}).
Brand Tagline: "{BRAND['tagline']}"
Target Audience: High-value Western founders and executives in the US, UK, and Europe across 3 pillars:
1. E-commerce / Shopify Brand Owners ($50k-$500k/mo)
2. B2B SaaS & Tech Startups
3. US Local Service Businesses (Real estate, medspas, high-ticket legal/home services)

Voice & Tone: Native Silicon Valley / Western B2B agency tone. Authoritative, sharp, data-driven, results-oriented, zero fluff.
Aesthetic & Identity: Tri-Color Feed Rhythm (Stealth Charcoal, Clean Editorial Light, High-Impact Orange).

2026 INSTAGRAM & META ALGORITHM GUIDELINES:
1. Short, Punchy Micro-Captions: Maximum 3 to 4 short lines total. Line 1: Strong hook. Line 2-3: Core actionable takeaway. No long essays or bulky bullet points.
2. Natural Semantic Keywords: Address the specific business problem naturally without keyword stuffing.
3. Strict 3-4 Clean Hashtags: Generate strictly 3-4 hyper-targeted, relevant hashtags. Never spam or hashtag-stuff.
"""

def call_gemini(prompt: str, system_instruction: str = SYSTEM_PROMPT, response_mime_type: str = "application/json") -> str:
    """Calls Gemini with exponential backoff and multi-model fallback for 100% reliability."""
    import time
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured in .env file.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7,
        response_mime_type=response_mime_type
    )

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.8-flash",
        "gemini-flash-latest",
        "gemini-flash-lite-latest"
    ]

    last_error = None
    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                if response.text and response.text.strip():
                    return response.text
            except Exception as e:
                last_error = e
                err_str = str(e)
                # If high demand / 503 or 429 rate limit, wait and retry
                if "503" in err_str or "429" in err_str or "UNAVAILABLE" in err_str:
                    wait_sec = 3 * (attempt + 1)
                    print(f"[Gemini Notice] Model {model_name} busy (503/429). Retrying in {wait_sec}s...")
                    time.sleep(wait_sec)
                else:
                    print(f"[Gemini Notice] Model {model_name} error: {e}. Moving to fallback model...")
                    break

    raise RuntimeError(f"All Gemini models exhausted. Last error: {last_error}")

def get_emergency_fallback_pack(target_niche: str = "B2B SaaS & High-Growth Brands") -> dict:
    """Deterministic, high-converting emergency content pack in case Gemini API is globally unavailable."""
    pillar = get_current_pillar()
    services = pillar.get("services_mentioned", ["AI Automation", "Conversion Optimization"])
    srv_str = " & ".join(services[:2]) if services else "Digital Growth"

    return {
        "story": {
            "headline": f"Is Your {srv_str} Automated Yet?",
            "poll_question": f"How is your team handling {srv_str} in 2026?",
            "poll_opt_a": "Manual / Time-Consuming",
            "poll_opt_b": "Automated AI Systems",
            "action_sticker": "TAP FOR STRATEGY ➔"
        },
        "reel": {
            "topic": f"Scaling {target_niche} with {srv_str}",
            "hook_3s": "Stop Doing This Manually.",
            "voiceover_script": "If your team is still spending hours on manual workflows, you are leaking margins. Deploy autonomous digital systems and scale seamlessly.",
            "b_roll_visuals": "Kinetic typography, high-contrast dark and orange UI elements, sleek motion graphics",
            "caption": f"Manual tasks cap your revenue ceiling. 2026 belongs to businesses with autonomous operations.\n\nHere is how {BRAND['name']} builds scalable architectures that run 24/7.",
            "cta_trigger_word": "SCALE",
            "hashtags": ["#AIAutomation", "#BusinessGrowth", "#KnownByDigital"]
        },
        "single_post": {
            "headline": f"Why 90% of {target_niche} Hit a Growth Wall at 6-Figures",
            "image_card_title": "Architecture Over Hustle",
            "image_card_subtitle": f"The 2026 Blueprint for {target_niche}",
            "caption": f"Most founders think they need more leads. In reality, they need better infrastructure.\n\nWhen your intake, conversion, and fulfillment run on high-performance systems, scale becomes predictable.\n\nAudit your core bottlenecks before spending another dollar on traffic.",
            "threads_version": f"Hustle does not scale. Systems do. Automate your {srv_str} before burning out your team.",
            "cta_trigger_word": "SYSTEM",
            "hashtags": ["#DigitalStrategy", "#ConversionOptimization", "#KnownByDigital"]
        },
        "carousel": {
            "topic": f"The 5-Step System Architecture for {target_niche}",
            "slides": [
                {
                    "slide_number": 1,
                    "type": "cover",
                    "headline": "The Modern Scalable Tech Stack",
                    "subheadline": f"How Leading {target_niche} Automate Growth (Swipe ➔)"
                },
                {
                    "slide_number": 2,
                    "type": "problem",
                    "headline": "The Disconnected Stack Trap",
                    "points": ["Scattered tools creating communication silos", "Wasted hours on manual data re-entry"]
                },
                {
                    "slide_number": 3,
                    "type": "solution_framework",
                    "headline": "The Unified Pipeline Engine",
                    "points": ["Single source of truth CRM integration", "Autonomous lead qualification & routing", "Zero-friction client onboarding"]
                },
                {
                    "slide_number": 4,
                    "type": "case_study_metric",
                    "headline": "Measured Impact",
                    "points": ["3.4x faster pipeline throughput", "Zero dropped inbound leads", "40+ hours saved every month"]
                },
                {
                    "slide_number": 5,
                    "type": "cta",
                    "headline": "Build Your Private Engine",
                    "subheadline": f"Comment 'GROWTH' below or DM @knownbydigital to map your custom blueprint."
                }
            ],
            "caption": f"Stop stitching together disconnected tools. Build an integrated system designed to scale effortlessly.",
            "cta_trigger_word": "GROWTH",
            "hashtags": ["#OperationsScale", "#B2BStrategy", "#KnownByDigital"]
        }
    }

from topic_memory import get_recent_topics, get_current_pillar, record_published_pack

def generate_daily_social_pack(target_niche: str = None) -> dict:
    """
    Generates a full daily content pack with 2026 SEO Optimization & Anti-Repetition Memory:
    1. Faceless Trendy Reel (Script, Hook, Audio, B-roll cues, Caption, Researched Hashtags)
    2. Single Insight Post (Headline, Body, Image Card Text, Caption, Researched Hashtags)
    3. Multi-Slide Carousel (5-6 Slides, Caption, Researched Hashtags)
    4. Interactive Story (Poll / Quiz card with KBD Branding)
    """
    if not target_niche:
        import random
        target_niche = random.choice(BRAND["target_niches"])

    current_month_year = datetime.now().strftime('%B %Y')
    recent_topics = get_recent_topics(limit=35)
    pillar = get_current_pillar()

    exclusion_text = "\n".join([f"- {t}" for t in recent_topics[:25]]) if recent_topics else "- None yet (Brand new cycle)."

    prompt = f"""
Generate today's complete SEO-optimized social media content pack for {BRAND['name']}.
Focus Niche: {target_niche}.
Today's Strategic Content Pillar: {pillar['name']}
Pillar Description & Focus: {pillar['focus']}
Core Services Highlighted: {', '.join(pillar['services_mentioned'])}
Date Context: {current_month_year} (Targeting 2026 Meta/Instagram Algorithm).

CRITICAL ANTI-REPETITION & TOPIC DIVERSITY RULES:
1. STRICT TOPIC EXCLUSION (DO NOT REPEAT):
The following topics have already been used recently. DO NOT repeat, re-use, or closely paraphrase any of them:
{exclusion_text}

2. FORMAT DIVERSITY (ZERO SAME-DAY OVERLAP):
Each of the 4 formats (Story, Single Post, Carousel, Reel) MUST cover a DIFFERENT, UNIQUE angle today:
- If Reel covers Autonomous AI Intake, Single Post must cover Website Conversion Architecture / CRO, Carousel must cover an Operations SOP, and Story must cover an interactive poll. NEVER have all formats discuss the identical topic!

3. SERVICE & OFFER INTEGRATION:
Naturally weave in Known By Digital's real services: Website Design/Development, AI Automation, CRM Workflows, and Free 1-on-1 Growth Architecture Audits.

CAPTION STRATEGY (CRITICAL ALGORITHM COMPLIANCE):
1. SINGLE POST CAPTION (Medium-length Micro-Blog, 80-130 words):
   - The single post image is a sleek, minimal headline card. Therefore, the caption MUST provide the deep-dive context and strategic value!
   - Paragraph 1: Hard-hitting contrarian hook expanding on the headline.
   - Paragraph 2: Core breakdown or tactical diagnosis (2-3 structured bullet points with ➔ or •).
   - Paragraph 3: Actionable founder takeaway.
   - Word count: 80 to 130 words. Clean, authoritative, highly readable.

2. REEL & CAROUSEL CAPTIONS (Short & Punchy, 2-3 short lines):
   - Keep strictly concise (2-3 short lines total). The video audio and carousel slides already contain the content.
   - Line 1: Strong hook. Line 2-3: Core takeaway. Readable in 3 seconds.

3. REEL DURATION (CRITICAL: STRICTLY 7 TO 15 SECONDS):
   - The "voiceover_script" MUST be strictly 20 to 28 words maximum (approx. 8 to 12 seconds spoken duration).
   - Fast-paced, punchy, high-impact narration. No filler.
   - Never exceed 30 words so the entire Reel stays strictly between 7 to 15 seconds for maximum viral loop completion!

4. HASHTAGS (STRICTLY 3-4 PER POST):
   - Generate strictly 3-4 hyper-targeted, relevant hashtags in the "hashtags" array (e.g. #AIAutomation #WebDesign #KnownByDigital). NO hashtag stuffing!

Return a strict JSON object with this EXACT schema:
{{
  "pillar_used": "{pillar['name']}",
  "story": {{
    "tag": "TODAY'S GROWTH POLL",
    "headline": "Punchy 6-9 word question or insight",
    "poll_opt_a": "Status-quo / Manual alternative",
    "poll_opt_b": "Modern AI / High-performance alternative",
    "action_sticker": "TAP TO WATCH NEW REEL ➔"
  }},
  "reel": {{
    "topic": "Distinct video topic (under the pillar)",
    "hook_3s": "High-impact pattern-interrupt text (max 6 words)",
    "voiceover_script": "Strictly 20-28 words (8-12 seconds duration) fast-paced narrator script",
    "b_roll_visuals": "Canva-style kinetic tech visuals",
    "caption": "Short, punchy 2-3 line caption focusing on the core revenue insight",
    "cta_trigger_word": "SYSTEM",
    "hashtags": ["#AIAutomation", "#B2BGrowth", "#KnownByDigital"]
  }},
  "single_post": {{
    "headline": "Bold contrarian headline (distinct from Reel topic)",
    "image_card_title": "Punchy card text (max 5 words)",
    "image_card_subtitle": "Secondary supporting insight (max 8 words)",
    "caption": "Medium-length micro-blog caption (80-130 words) with hook, 2-3 structured bullet points, and takeaway",
    "threads_version": "Under 250-character punchy one-liner version",
    "cta_trigger_word": "AUDIT",
    "hashtags": ["#WebDevelopment", "#ConversionRate", "#KnownByDigital"]
  }},
  "carousel": {{
    "topic": "Actionable SOP / Playbook topic (distinct from Reel and Single Post)",
    "slides": [
      {{
        "slide_number": 1,
        "type": "cover",
        "headline": "Big Hook Title (e.g. The 2026 High-Converting Tech Stack)",
        "subheadline": "How 7-Figure Brands Scale Without Overhead (Swipe ->)"
      }},
      {{
        "slide_number": 2,
        "type": "problem",
        "headline": "The Silent Margin Killer",
        "points": ["Point 1 breakdown", "Point 2 breakdown"]
      }},
      {{
        "slide_number": 3,
        "type": "solution_framework",
        "headline": "The 3-Step Execution Model",
        "points": ["Step 1: Architecture", "Step 2: Deployment", "Step 3: CRM Loop"]
      }},
      {{
        "slide_number": 4,
        "type": "case_study_metric",
        "headline": "Measurable Results",
        "points": ["+42% Pipeline Speed", "-60% Manual Chasing"]
      }},
      {{
        "slide_number": 5,
        "type": "cta",
        "headline": "Make Your Brand AI-Ready",
        "subheadline": "Comment 'SYSTEM' below or DM @knownbydigital to claim your custom roadmap."
      }}
    ],
    "caption": "Short, punchy 2-3 line playbook caption with swipe prompt",
    "cta_trigger_word": "SYSTEM",
    "hashtags": ["#BusinessOperations", "#AgencyScale", "#KnownByDigital"]
  }}
}}
"""
    try:
        raw_json = call_gemini(prompt)
        pack = json.loads(raw_json)
        record_published_pack(pack)
        return pack
    except Exception as e:
        print(f"[ContentEngine Warning] Gemini call failed ({e}). Activating Emergency Strategic Content Pack...")
        pack = get_emergency_fallback_pack(target_niche)
        return pack

def assemble_seo_caption(post_obj: dict) -> str:
    """
    Combines clean, punchy copy, a 1-line website/SOP CTA,
    and strictly 3-4 targeted hashtags (zero clutter).
    """
    base_caption = post_obj.get("caption", "").strip()
    trigger = post_obj.get("cta_trigger_word", "SYSTEM")
    hashtags = post_obj.get("hashtags", [])

    clean_tags = []
    for h in hashtags:
        tag = h.strip()
        if not tag.startswith("#"):
            tag = f"#{tag}"
        if tag not in clean_tags:
            clean_tags.append(tag)
        if len(clean_tags) >= 3:
            break

    if "#KnownByDigital" not in clean_tags:
        clean_tags.append("#KnownByDigital")

    tag_str = " ".join(clean_tags[:4])
    cta_line = f"🔗 {BRAND['website']} • Comment '{trigger}' or DM us for the private SOP."

    return f"{base_caption}\n\n{cta_line}\n\n{tag_str}"

if __name__ == "__main__":
    print("Testing Daily Social Pack with SEO engine...")
    p = generate_daily_social_pack()
    print("SEO Caption sample:\n", assemble_seo_caption(p["single_post"])[:200])
