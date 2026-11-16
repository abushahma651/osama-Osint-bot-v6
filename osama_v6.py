from flask import Flask
import threading
import os
import telebot
import requests
import time
import json
from telebot import types

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
YOUR_CHAT_ID = str(os.environ.get('CHAT_ID'))
API_BASE_URL = "https://api.darknetwork.site/index.php?api=hi_tek&key=key_DarkApiX444&search={}"

bot = telebot.TeleBot(BOT_TOKEN)

# --- DATABASE (Temporary Memory) ---
USER_DATA = {} 
SEARCH_HISTORY = {} 
PROTECTED_NUMBERS = ["9621303160", "7991536322", "8604302624", "6204473620"]

# =====================================================================
# 👇 VIP ACCESS LIST (Authorized Members) 👇
# =====================================================================
ALLOWED_USERS = [
    YOUR_CHAT_ID,       # Owner (Aap)
    "8707785706", "8898567917", "6700078527",
    "5704555109", "901112667", "8659201578"
]

def is_authorized(user_id):
    return str(user_id) in ALLOWED_USERS

def get_user_credits(user_id):
    user_id = str(user_id)
    if user_id == YOUR_CHAT_ID:
        return "Unlimited"
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {"credits": 5, "last_claim": 0}
    return USER_DATA[user_id]["credits"]

# --- KEYBOARDS (NEW PREMIUM MENU) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔍 Num Lookup", "🧠 TG ID → Num")
    markup.row("👤 TG User → Num", "📁 Num → All Info")
    markup.row("🪪 Aadhaar Info", "👥 Aadhaar Family")
    markup.row("📧 Email → Num", "🌐 Web Scraper")
    markup.row("🚗 Vehicle → Num", "🏡 Vehicle Address")
    markup.row("📄 RC → PDF", "🚨 Vehicle Challan")
    markup.row("📸 Instagram Info", "📝 Name → Random Info")
    markup.row("🆔 Aadhaar → Ration", "💳 PAN Info")
    markup.row("⚪ LPG Info", "🚙 Num → Vehicle")
    markup.row("🎮 BGMI Info", "✨ Features") # Changed FF to BGMI
    markup.row("📖 How to Use", "📊 My Credits")
    markup.row("🛒 Buy Credits", "🎁 Daily Claim")
    markup.row("🎁 Refer & Earn", "🔗 Share Bot")
    return markup

def result_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_dev = types.InlineKeyboardButton("👨‍💻 Contact Developer (NERD)", url=f"tg://user?id={YOUR_CHAT_ID}")
    markup.add(btn_dev)
    return markup

# --- ACCESS DENIED HELPER ---
def send_access_denied(message):
    text = (
        "🚫 <b>ACCESS DENIED</b>\n\n"
        "This is a private NERD OSINT tool. You don't have permission to use it.\n\n"
        "❌ <b>You don't have credits.</b>\n"
        "To get VIP access and credits, contact NERD via the button below."
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=result_menu())

# --- AUTO DELETE ---
def delete_message_later(chat_id, message_id, delay=60):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except Exception:
        pass

# --- START COMMAND (PREMIUM INTERFACE) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    
    # Referral Logic
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        referrer_id = args[1].replace("ref_", "")
        if referrer_id != user_id and referrer_id in ALLOWED_USERS:
            if referrer_id not in USER_DATA:
                USER_DATA[referrer_id] = {"credits": 5, "last_claim": 0}
            USER_DATA[referrer_id]["credits"] += 5
            try:
                bot.send_message(referrer_id, f"🎉 <b>Referral Bonus!</b>\nYou earned 5 credits because {first_name} joined using your link.", parse_mode='HTML')
            except Exception:
                pass

    # Premium Image (Cyber Security Theme)
    image_url = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
    
    if is_authorized(user_id):
        credits = get_user_credits(user_id)
        text = (
            f"👋 <b>Welcome, {first_name}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "✨ <b>What can this bot do?</b>\n\n"
            "🔍 <b>OSINT INTELLIGENCE</b>\n"
            "🌐 Open Source Intelligence\n"
            "📱 Number • Username • Domain\n"
            "📊 Data Discovery • Verification\n"
            "⚡ Fast • Smart • Reliable\n\n"
            f"💳 <b>Your Credits:</b> {credits}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "👑 <b>OWNER</b> — @OSMIUM_9\n"
            "🛡 Privacy • Responsible OSINT\n"
            "⚠️ <i>Only for lawful research & verified use.</i>"
        )
    else:
        text = (
            f"👋 <b>Welcome, {first_name}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "✨ <b>What can this bot do?</b>\n\n"
            "🔍 <b>OSINT INTELLIGENCE</b>\n"
            "🌐 Open Source Intelligence\n"
            "📱 Number • Username • Domain\n"
            "📊 Data Discovery • Verification\n"
            "⚡ Fast • Smart • Reliable\n\n"
            "🔒 <i>VIP Access required for searching.</i>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "👑 <b>OWNER</b> — @OSMIUM_9\n"
            "🛡 Privacy • Responsible OSINT\n"
            "⚠️ <i>Only for lawful research & verified use.</i>"
        )

    # Send Photo with Caption and Menu
    bot.send_photo(message.chat.id, image_url, caption=text, parse_mode='HTML', reply_markup=main_menu())

# --- HOW TO USE ---
@bot.message_handler(func=lambda message: message.text == "📖 How to Use")
def how_to_use(message):
    text = (
        "📖 <b>*HOW TO USE*</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "1️⃣ Feature button select karo\n"
        "2️⃣ Information bhejo (number, id, etc.)\n"
        "3️⃣ 1 credit per search\n"
        "4️⃣ Daily claim se free credits lo\n"
        "5️⃣ Share bot for +1 credit per friend\n\n"
        "Support: @OSMIUM_9"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())

# --- FEATURES LIST ---
@bot.message_handler(func=lambda message: message.text == "✨ Features")
def features_list(message):
    text = (
        "✨ <b>ALL FEATURES</b> ✨\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔍 Num Lookup\n"
        "🧠 TG ID → Num\n"
        "👤 TG User → Num\n"
        "📁 Num → All Info\n"
        "🪪 Aadhaar Info\n"
        "👥 Aadhaar Family\n"
        "📧 Email → Num\n"
        "🌐 Web Scraper\n"
        "🚗 Vehicle → Num\n"
        "🏡 Vehicle Address\n"
        "📄 RC → PDF\n"
        "🚨 Vehicle Challan\n"
        "📸 Instagram Info\n"
        "📝 Name → Random Info\n"
        "🆔 Aadhaar → Ration\n"
        "💳 PAN Info\n"
        "⚪ LPG Info\n"
        "🚙 Num → Vehicle\n"
        "🎮 BGMI Info\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👑 Contact @OSMIUM_9"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())

# --- SHARE BOT ---
@bot.message_handler(func=lambda message: message.text == "🔗 Share Bot")
def share_bot(message):
    bot_info = bot.get_me()
    link = f"https://t.me/{bot_info.username}"
    text = (
        "🔗 <b>Share NERD OSINT</b>\n\n"
        "Share this bot with your friends and earn credits!\n\n"
        f"<code>{link}</code>"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())

# --- BUY CREDITS ---
@bot.message_handler(func=lambda message: message.text == "🛒 Buy Credits")
def buy_credits(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    text = (
        "🛒 <b>Buy Credits</b>\n\n"
        "To purchase more credits, please contact the developer directly.\n"
        "Click the button below to message NERD."
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=result_menu())

# --- REFER & EARN ---
@bot.message_handler(func=lambda message: message.text == "🎁 Refer & Earn")
def refer_earn(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    user_id = str(message.from_user.id)
    bot_info = bot.get_me()
    link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
    
    text = (
        "🎁 <b>Refer & Earn</b>\n\n"
        "Invite your friends to NERD PRIVATE OSINT.\n"
        "You get <b>5 Credits</b> for every friend who joins using your link!\n\n"
        f"🔗 <b>Your Link:</b>\n<code>{link}</code>"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())

# --- DAILY CLAIM ---
@bot.message_handler(func=lambda message: message.text == "🎁 Daily Claim")
def daily_claim(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    user_id = str(message.from_user.id)
    if user_id == YOUR_CHAT_ID:
        bot.reply_to(message, "👑 <b>Owner has Unlimited Credits!</b>", parse_mode='HTML', reply_markup=main_menu())
        return

    if user_id not in USER_DATA:
        USER_DATA[user_id] = {"credits": 0, "last_claim": 0}

    current_time = time.time()
    last_claim = USER_DATA[user_id]["last_claim"]
    
    if current_time - last_claim < 86400:
        remaining = 86400 - (current_time - last_claim)
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        bot.reply_to(message, f"⏳ <b>Already Claimed!</b>\nCome back in {hours}h {minutes}m to claim again.", parse_mode='HTML', reply_markup=main_menu())
        return
        
    USER_DATA[user_id]["credits"] += 10
    USER_DATA[user_id]["last_claim"] = current_time
    bot.reply_to(message, f"🎉 <b>Claim Successful!</b>\nYou got 10 credits. Total: {USER_DATA[user_id]['credits']}", parse_mode='HTML', reply_markup=main_menu())

# --- CHECK CREDITS ---
@bot.message_handler(func=lambda message: message.text == "📊 My Credits")
def check_credits(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    credits = get_user_credits(message.from_user.id)
    bot.reply_to(message, f"💳 <b>Your Balance:</b> {credits}\n\nContact NERD to buy more credits.", parse_mode='HTML', reply_markup=main_menu())

# --- WORKING API PROMPTS ---
# Mapping "🔍 Num Lookup" to Indian Number API
@bot.message_handler(func=lambda message: message.text in ["🔍 Num Lookup", "📁 Num → All Info"])
def prompt_mobile(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    msg = bot.reply_to(message, "📱 <b>Enter a 10-digit Mobile Number to search:</b>", parse_mode='HTML', reply_markup=main_menu())
    bot.register_next_step_handler(msg, process_search, "MOBILE")

# Mapping "🪪 Aadhaar Info" to Aadhaar API
@bot.message_handler(func=lambda message: message.text == "🪪 Aadhaar Info")
def prompt_aadhaar(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    msg = bot.reply_to(message, "🆔 <b>Enter a 12-digit Aadhaar Number to search:</b>", parse_mode='HTML', reply_markup=main_menu())
    bot.register_next_step_handler(msg, process_search, "AADHAAR")

# --- "COMING SOON" HANDLER (Rest of the buttons) ---
@bot.message_handler(func=lambda message: message.text in [
    "🧠 TG ID → Num", "👤 TG User → Num", "👥 Aadhaar Family", "📧 Email → Num", 
    "🌐 Web Scraper", "🚗 Vehicle → Num", "🏡 Vehicle Address", "📄 RC → PDF", 
    "🚨 Vehicle Challan", "📸 Instagram Info", "📝 Name → Random Info", 
    "🆔 Aadhaar → Ration", "💳 PAN Info", "⚪ LPG Info", "🚙 Num → Vehicle", "🎮 BGMI Info"
])
def coming_soon(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    bot.reply_to(message, "⚠️ <b>Soon this service will start.</b>\nStay tuned for the next update by NERD.", parse_mode='HTML', reply_markup=main_menu())

# --- MAIN SEARCH FUNCTION ---
def process_search(message, query_type, direct_query=None):
    user_id = str(message.from_user.id)
    if not is_authorized(user_id):
        return send_access_denied(message)

    query = direct_query if direct_query else message.text.strip()
    
    if query in ["🔍 Num Lookup", "📁 Num → All Info", "🪪 Aadhaar Info"]:
        bot.send_message(message.chat.id, "Please enter the number.", reply_markup=main_menu())
        return
        
    if query_type == "MOBILE" and (not query.isdigit() or len(query) != 10):
        bot.reply_to(message, "❌ Invalid mobile number.", reply_markup=main_menu())
        return
    if query_type == "AADHAAR" and (not query.isdigit() or len(query) != 12):
        bot.reply_to(message, "❌ Invalid Aadhaar number.", reply_markup=main_menu())
        return

    # 💳 CHECK & DEDUCT CREDITS
    if user_id != YOUR_CHAT_ID:
        if user_id not in USER_DATA:
            USER_DATA[user_id] = {"credits": 5, "last_claim": 0}
        if USER_DATA[user_id]["credits"] < 1:
            bot.reply_to(message, "❌ <b>You need 1 credit for this.</b>\nUse Daily Claim or Contact NERD.", parse_mode='HTML', reply_markup=main_menu())
            return
        USER_DATA[user_id]["credits"] -= 1

    # 🔥 SAVE TO HISTORY
    if user_id not in SEARCH_HISTORY:
        SEARCH_HISTORY[user_id] = []
    SEARCH_HISTORY[user_id].append(query)

    if query in PROTECTED_NUMBERS:
        bot.reply_to(message, "🚫 Protected Identity.", reply_markup=main_menu())
        return
        
    msg = bot.send_message(message.chat.id, f"⚡ <b>Searching {query_type} for:</b> <code>{query}</code>\n\n<code>[■□□□□□□□□□] INITIALIZING...</code>", parse_mode='HTML')
    
    for stage in ["> [■■■□□□□□□□] BYPASSING FIREWALLS...", "> [■■■■■■■■□□] EXTRACTING RECORDS..."]:
        time.sleep(0.5)
        bot.edit_message_text(f"⚡ <b>Searching:</b> <code>{query}</code>\n\n<code>{stage}</code>", message.chat.id, msg.message_id, parse_mode='HTML')
        
    records = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(API_BASE_URL.format(query), headers=headers, timeout=60)
        if res.status_code == 200:
            data = res.json()
            if data.get('status') == 'success' and 'data' in data:
                records = data['data']
    except Exception: pass
            
    if records:
        record = records[0]
        name = record.get('name', 'N/A')
        fname = record.get('fname', 'N/A')
        mobile = record.get('mobile', query if query_type == "MOBILE" else 'N/A')
        alt = record.get('alt', 'None')
        if alt == 'None' or not alt: alt = 'N/A'
        aadhaar = record.get('id', query if query_type == "AADHAAR" else 'N/A')
        address = record.get('address', 'N/A')
        clean_address = address.replace('!', ', ').strip(', ') if address != 'N/A' else 'N/A'

        curr_cred = "Unlimited" if user_id == YOUR_CHAT_ID else USER_DATA[user_id]["credits"]

        report = (
            "<pre>"
            "NERD PRIVATE OSINT REPORT\n\n"
            f"👤 Query        : {query}\n"
            f"📊 Type         : {query_type}\n"
            "------------------------------\n"
            f"Name           : {name}\n"
            f"Father Name    : {fname}\n"
            f"Mobile         : {mobile}\n"
            f"Alt Number     : {alt}\n"
            f"Aadhaar No     : {aadhaar}\n"
            f"Address        : {clean_address}\n"
            "------------------------------\n"
            f"Credits Left   : {curr_cred}\n"
            "By : @OSMIUM_9\n"
            "</pre>\n\n"
            "⚠️ <b>NOTE:</b> <i>This report will be auto-deleted in 60 seconds. Save it before it gets deleted!</i>"
        )
        
        sent_msg = bot.edit_message_text(report, message.chat.id, msg.message_id, parse_mode='HTML', reply_markup=result_menu())
        threading.Thread(target=delete_message_later, args=(message.chat.id, sent_msg.message_id, 60)).start()
        
    else:
        sent_msg = bot.edit_message_text(
            text=f"🔴 <b>DATA NOT FOUND:</b> <code>{query}</code>\n\n<i>No records found.</i>",
            chat_id=message.chat.id, message_id=msg.message_id, parse_mode='HTML', reply_markup=result_menu()
        )
        threading.Thread(target=delete_message_later, args=(message.chat.id, sent_msg.message_id, 60)).start()

# --- INVALID INPUT HANDLER ---
@bot.message_handler(func=lambda message: True)
def invalid_input(message):
    if not is_authorized(message.from_user.id): 
        return send_access_denied(message)
    bot.reply_to(message, "❌ Please use the menu below.", reply_markup=main_menu())

# --- WEB SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "NERD PRIVATE OSINT Premium Bot is running!"
def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    print("🤖 NERD PRIVATE OSINT Premium is running...")
    bot.polling(none_stop=True)
