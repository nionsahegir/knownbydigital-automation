@echo off
title Known By Digital - Social Automation Daemon
echo ============================================================
echo   KNOWN BY DIGITAL // SOCIAL AUTOMATION RUNNER
echo ============================================================
echo Starting 24/7 background scheduler...
echo - Daily Post Trigger: 19:00 BST (9:00 AM EST)
echo - Comment Polling: Every 15 minutes (with Anti-Ban delays)
echo - Auto-Cleaner: Enforces strict 48-hour retention
echo ============================================================

set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
cd /d "%~dp0"

"%PYTHON_EXE%" daemon_scheduler.py
pause
