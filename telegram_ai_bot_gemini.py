"""
Automatic AI Telegram Bot (Gemini free API se)
-------------------------------------------------
Ye bot Telegram par aane wale har message ka automatically AI se reply deta hai.
Deploy karne ke baad ye 24/7 khud chalta rehta hai.

SETUP:
1) pip install -r requirements.txt
2) Neeche AGENT_ROLE line change karo (bot kis kaam ke liye hai)
3) Is file ko Render.com / Railway.app pe "Background Worker" ke roop mein deploy karo
4) Bas - deploy hote hi bot live ho jayega

Free Gemini API ki daily limit hoti hai (kaafi generous hai chhoti bot ke liye),
agar limit khatam ho jaye to agle din reset ho jati hai.
"""

import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters

# ============ AAPKI DETAILS (already bhari hui hain) ============
BOT_TOKEN = "8837999324:AAEypJqN1hFS8RCPG3C0u9K6sQp1fpUSPGw"
GEMINI_API_KEY = "AIzaSyC1S6mH3q-va1fEDD9ZX_9RYwQmjPfJqko"
AGENT_ROLE = "Ek friendly business assistant jo customers ke sawalon ka Hinglish mein jawab deta hai, orders leta hai, aur pricing/timing ki info deta hai."
# ==================================================================

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# Har user ki conversation history yaad rakhne ke liye
user_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Namaste! Main aapka automatic assistant hoon. Kuch bhi pucho, main madad karunga."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({"role": "user", "parts": [{"text": user_text}]})
    user_histories[user_id] = user_histories[user_id][-10:]  # sirf last 10 messages yaad

    system_instruction = (
        f"You are an AI agent operating in this role: {AGENT_ROLE}. "
        f"Reply naturally in the language the user writes in (Hindi, Hinglish, or English). "
        f"Keep replies short and helpful, like a real chat conversation."
    )

    payload = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": user_histories[user_id]
    }

    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=30)
        data = response.json()

        reply_text = data["candidates"][0]["content"]["parts"][0]["text"]

        user_histories[user_id].append({"role": "model", "parts": [{"text": reply_text}]})
        await update.message.reply_text(reply_text)

    except Exception as e:
        await update.message.reply_text("Maaf kijiye, thodi dikkat aa gayi. Thodi der baad try karein.")
        print(f"Error: {e} | Response: {response.text if 'response' in dir() else 'no response'}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot chalu ho gaya hai aur messages ka wait kar raha hai...")
    app.run_polling()

if __name__ == "__main__":
    main()
