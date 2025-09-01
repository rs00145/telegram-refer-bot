import os
import telebot
from telebot import types
from flask import Flask, request

# 🔹 Bot Config (Environment Variables me set karna hoga)
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL")
ADMIN_ID = 5717301873   # ✅ Admin ka Telegram User ID

bot = telebot.TeleBot(TOKEN)

# Users data store
users = {}  # {user_id: {"referrals":0, "balance":0, "method":"", "details":""}}

# Start Command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)

    if user_id not in users:
        users[user_id] = {"referrals": 0, "balance": 0, "method": "", "details": ""}

    # 🔹 Force Subscribe Check
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        if member.status not in ['member', 'administrator', 'creator']:
            return send_join_message(message)
    except:
        return send_join_message(message)

    # 🔹 Referral System
    args = message.text.split()
    if len(args) > 1:
        referrer = args[1]
        if referrer != user_id:
            if referrer in users:
                users[referrer]["referrals"] += 1
                users[referrer]["balance"] += 5  # ₹5 per referral
                bot.send_message(referrer, f"🎉 Aapko ek new referral mila!\n💰 Balance: ₹{users[referrer]['balance']}")

    bot.reply_to(
        message,
        f"👋 Welcome {message.from_user.first_name}!\n\n"
        f"🔗 Aapka referral link:\n"
        f"https://t.me/{bot.get_me().username}?start={user_id}\n\n"
        f"👥 Referrals: {users[user_id]['referrals']}\n"
        f"💰 Balance: ₹{users[user_id]['balance']}"
    )

# 🔹 Send join message
def send_join_message(message):
    markup = types.InlineKeyboardMarkup()
    join_button = types.InlineKeyboardButton("📢 Channel Join Karo", url=f"https://t.me/{CHANNEL[1:]}")
    refresh_button = types.InlineKeyboardButton("🔄 Check Again", callback_data="check")
    markup.add(join_button, refresh_button)
    bot.send_message(message.chat.id, "❌ Pehle channel join karo tabhi bot use kar sakte ho.", reply_markup=markup)

# 🔹 Callback handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "check":
        start(call.message)
    elif call.data.startswith("approve_"):
        user_id = call.data.split("_")[1]
        if str(call.from_user.id) == str(ADMIN_ID):
            users[user_id]["balance"] = 0
            bot.send_message(user_id, "✅ Aapka withdraw successful hai. Jaldi aapko payment mil jaayega.")
            bot.edit_message_text("✅ Withdraw Approved!", call.message.chat.id, call.message.message_id)
    elif call.data.startswith("deny_"):
        user_id = call.data.split("_")[1]
        if str(call.from_user.id) == str(ADMIN_ID):
            bot.send_message(user_id, "❌ Aapka withdraw reject kar diya gaya.")
            bot.edit_message_text("❌ Withdraw Denied!", call.message.chat.id, call.message.message_id)

# 🔹 Balance Command
@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = str(message.from_user.id)
    bal = users.get(user_id, {"balance": 0})["balance"]
    bot.send_message(message.chat.id, f"💰 Aapka Balance: ₹{bal}")

# 🔹 Refer Count
@bot.message_handler(commands=['refercount'])
def refercount(message):
    user_id = str(message.from_user.id)
    refs = users.get(user_id, {"referrals": 0})["referrals"]
    bot.send_message(message.chat.id, f"👥 Aapke referrals: {refs}")

# 🔹 Profile
@bot.message_handler(commands=['profile'])
def profile(message):
    user_id = str(message.from_user.id)
    data = users.get(user_id, {"referrals": 0, "balance": 0})
    bot.send_message(message.chat.id,
                     f"👤 Profile\n\n"
                     f"🆔 User ID: {user_id}\n"
                     f"👥 Referrals: {data['referrals']}\n"
                     f"💰 Balance: ₹{data['balance']}")

# 🔹 Withdraw
@bot.message_handler(commands=['withdraw'])
def withdraw(message):
    user_id = str(message.from_user.id)
    bal = users.get(user_id, {"balance": 0})["balance"]

    if bal < 50:
        bot.send_message(message.chat.id, "❌ Minimum withdraw ₹50 hai.")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📲 UPI", callback_data="withdraw_upi"))
    markup.add(types.InlineKeyboardButton("💳 Paytm", callback_data="withdraw_paytm"))
    markup.add(types.InlineKeyboardButton("🏦 PhonePe", callback_data="withdraw_phonepe"))
    bot.send_message(message.chat.id, "✅ Withdraw method choose karo:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("withdraw_"))
def withdraw_method(call):
    method = call.data.split("_")[1]
    user_id = str(call.from_user.id)
    users[user_id]["method"] = method
    bot.send_message(call.message.chat.id, f"📩 Apna {method} number/ID bhejo:")
    bot.register_next_step_handler(call.message, save_withdraw_details, method)

def save_withdraw_details(message, method):
    user_id = str(message.from_user.id)
    details = message.text
    amount = users[user_id]["balance"]

    users[user_id]["details"] = details

    # Send request to Admin
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"))
    markup.add(types.InlineKeyboardButton("❌ Deny", callback_data=f"deny_{user_id}"))

    bot.send_message(ADMIN_ID,
                     f"🆕 Withdraw Request\n\n"
                     f"👤 User: {message.from_user.first_name} ({user_id})\n"
                     f"💰 Amount: ₹{amount}\n"
                     f"💳 Method: {method}\n"
                     f"📩 Details: {details}",
                     reply_markup=markup)

    bot.send_message(message.chat.id, "✅ Withdraw request admin ko bhej diya gaya. Jaldi review hoga.")

# 🔹 Flask App for Webhook
app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.stream.read().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.getenv('RENDER_URL')}/" + TOKEN)
    return "🤖 Bot webhook set ho gaya!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
