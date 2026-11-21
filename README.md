# Known By Digital - Social Media Automation Engine

AI-Powered, Omnichannel Content & Engagement Automation for Instagram, Facebook Page, and Threads.

---

## 🚀 Overview
- **AI Engine:** Google Gemini 2.5 Flash / Flash Lite (Fallback-enabled)
- **Target Audience:** US, UK, European Decision Makers (Shopify Brands, SaaS, US Local Services)
- **Cadence:** Daily at 19:00 BST (9:00 AM EST / 2:00 PM UK)
- **Safe Engagement:** Comment & DM monitoring every 15 minutes with humanized random delays (45-90s)
- **Auto-Cleaner:** Strict 48-hour (2-day) retention. Older files are automatically deleted to keep local storage clean.
- **Cloud-Ready:** Includes `Dockerfile` and `docker-compose.yml` for 1-click cloud deployment.

---

## 📁 Project Structure
```
knownbydigital_automation/
├── .env                       # API keys and tokens (Gemini API key is configured!)
├── config.py                  # Brand styling, palette (#040229), and settings
├── cleaner.py                 # Auto-deletes generated media older than 48 hours
├── content_engine.py          # Google Gemini AI copywriter for Reel, Post, Carousel
├── media_generator.py         # Pillow-based dark-theme card and carousel slide generator
├── meta_publisher.py          # Meta Graph API & Threads publisher
├── engagement_bot.py          # Safe 15-minute comment auto-replier
├── run_daily_pipeline.py      # Main daily runner
├── daemon_scheduler.py        # 24/7 background scheduler
├── start_automation.bat       # One-click Windows starter
├── Dockerfile                 # For Cloud deployment
└── generated_media/           # Automatically cleaned output folder (keeps 48 hours only)
```

---

## 🔑 How to Add Meta Tokens (When You're Ready)
Open the `.env` file and fill in:
```ini
META_PAGE_ACCESS_TOKEN=your_token_here
FACEBOOK_PAGE_ID=your_page_id_here
INSTAGRAM_ACCOUNT_ID=your_ig_id_here
THREADS_USER_ID=your_threads_id_here
THREADS_ACCESS_TOKEN=your_threads_token_here
```
*(Until tokens are added, the system safely runs in Simulation Mode, generating and validating all media without throwing errors!)*

---

## ☁️ How to Move to Cloud After 1-2 Weeks
When you are ready to run this on a Cloud VPS (so your laptop can stay off):
```bash
docker build -t kbd-automation .
docker run -d --restart always --name kbd-bot kbd-automation
```
That's it! It will run 24/7 on the cloud unattended.
