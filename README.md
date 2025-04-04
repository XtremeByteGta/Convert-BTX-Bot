# 📌 Xtreme Bot Source Code  
🚀 **A Cool Telegram Bot by Xtreme Byte**  

---

## 🔥 What Can the Bot Do?  
This bot is packed with awesome features:  

- **1. BTX to PNG Conversion**  
  Drop a `.btx` file, and boom 💥 — you get a shiny `.png` back!  

- **2. ZIP Archive Processing**  
  Send a `.zip` with BTX files (up to 50 MB), and the bot unzips, converts, and hands you a ZIP full of PNGs.  

- **3. Link Handling**  
  Share a link to a `.btx` or `.zip` (like from Google Drive), and the bot downloads and processes it for you.  

- **4. Subscription Check**  
  Only subscribers of the set channel get access (customize it to your own channel!).  

### Commands  
- `/start` — Kick things off  
- `/info` — See what the bot can do  
- `/agreement` — Read the terms  
- `/feedback` — Send your thoughts  
- `/help` — Get detailed help  

---

## 🛠 How to Set Up Your Own Bot?  
Want to run your own version of this bot? Here’s the step-by-step:  

1. **Download the Code**  
   Grab it and let’s get started!  

2. **Install Dependencies**  
   Make sure you’ve got Python 3.7+. Then run:  
   
             pip install python-telegram-bot aiohttp

3. **Get a Bot Token**  
Chat with `@BotFather` on Telegram, use `/newbot` to create one, and copy the token. Replace `TOKEN = '1234567890987654321'` in the code with it.  

4. **Set Up Your Channel**  
Add your channel’s ID to `CHANNEL_ID = "@xtremebyte"`. The bot will check if users are subscribed.  
💡 Channel ID is the `@username` (e.g., `@xtremebyte`).  

5. **Add Your Admin ID**  
Set `ADMIN_ID = 123456789` to your Telegram ID (find it via `@userinfobot`). Errors and feedback will go here.  

6. **Include the Conversion Tool**  
The bot uses `convertNikeStudio.exe` for BTX processing. Make sure it’s in the same folder as `convert.py`.  

7. **Launch the Bot**  
Run the code, and if all’s good, your bot will spring to life! 😎  

---

## 💡 Handy Tips  
- Logs are saved in `bot.log` — super useful for debugging.  
- Temporary `user_<id>` folders are created for each user and cleaned up after processing.  

---

Enjoy the bot vibes! 🚀 **Xtreme Byte** gives it a thumbs-up! 👍  
