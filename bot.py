import os
import telebot
from telebot import types
from flask import Flask, request

# 🔹 Bot Config (Render/Heroku ke Environment Variables me set hoga)
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL")

bot = telebot.TeleBot(TOKEN)

# Dictionary to store referrals
referrals = {}

# Start Command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)

    # Check Force Subscribe
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        if member.status not in ['member', 'administrator', 'creator']:
            return send_join_message(message)
    except:
        return send_join_message(message)

    # Referral System
    args = message.text.split()
    if len(args) > 1:
        referrer = args[1]
        if referrer != user_id:  # Self referral not allowed
            referrals[referrer] = referrals.get(referrer, 0) + 1
            bot.send_message(referrer, f"🎉 Aapko ek new referral mila! Total: {referrals[referrer]}")

    bot.reply_to(
        message,
        f"👋 Welcome {message.from_user.first_name}!\n\n"
        f"🔗 Aapka referral link:\n"
        f"https://t.me/{bot.get_me().username}?start={user_id}\n\n"
        f"👥 Referrals: {referrals.get(user_id,0)}"
    )

# Send join message
def send_join_message(message):
    markup = types.InlineKeyboardMarkup()
    join_button = types.InlineKeyboardButton("📢 Channel Join Karo", url=f"https://t.me/{CHANNEL[1:]}")
    refresh_button = types.InlineKeyboardButton("🔄 Check Again", callback_data="check")
    markup.add(join_button, refresh_button)
    bot.send_message(message.chat.id, "❌ Pehle channel join karo tabhi bot use kar sakte ho.", reply_markup=markup)

# Refresh button
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "check":
        start(call.message)

# Flask App for Webhook
app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.stream.read().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://YOUR_RENDER_URL.onrender.com/" + TOKEN)
    return "Bot started ✅", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
