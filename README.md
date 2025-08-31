# Telegram Force Subscribe + Refer & Earn Bot

A simple Telegram bot that forces users to join your channel before using the bot, with referral system.

## 🚀 Setup Guide

### 1. Fork this repository
- Click the Fork button on top right.

### 2. Deploy on Heroku
1. Go to [Heroku](https://dashboard.heroku.com/) → Create new app.
2. Connect your GitHub repo.
3. In Settings → Reveal Config Vars:
   - `BOT_TOKEN` = Your BotFather token
   - `CHANNEL` = Your channel username (e.g. @MyChannel)
4. Deploy branch.

### 3. Enable Worker
- Go to Resources tab → Enable the worker dyno (`python bot.py`).

✅ Done! Your bot will run 24/7 on Heroku.
