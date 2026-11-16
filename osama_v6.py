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

# --- DATABASE ---
USER_DATA = {} 
SEARCH_HISTORY = {} 
PROTECTED_NUMBERS = ["9621303160", "7991536322", "8604302624", "6204473620"]

ALLOWED_USERS = [
    YOUR_CHAT_ID,       
    "8707785706", "8898567917", "6700078527",
    "5704555109", "901112667", "8659201578"
]

# Updated Button Texts (Clear LIVE / SOON status)
BTN_NUM = "✅ [LIVE] 📱 NUM LOOKUP"
BTN_AADHAAR = "✅ [LIVE] 🆔 AADHAAR INFO"

ALL_MENU_BUTTONS = [
    BTN_NUM, BTN_AADHAAR,
    "⏳ [SOON] 🧠 TG ID → Num", "⏳ [SOON] 👤 TG User → Num",
    "⏳ [SOON] 👥 Aadhaar Family", "⏳ [SOON] 📧 Email → Num",
    "⏳ [SOON] 🌐 Web Scraper", "⏳ [SOON] 🚗 Vehicle → Num",
    "⏳ [SOON] 🏡 Vehicle Address", "⏳ [SOON] 📄 RC → PDF",
    "⏳ [SOON] 🚨 Vehicle Challan", "⏳ [SOON] 📸 Instagram Info",
    "⏳ [SOON] 📝 Name → Random Info", "⏳ [SOON] 🆔 Aadhaar → Ration",
    "⏳ [SOON] 💳 PAN Info", "⏳ [SOON] ⚪ LPG Info",
    "⏳ [SOON] 🚙 Num → Vehicle", "⏳ [SOON] 🎮 BGMI Info",
    "✨ Features", "📖 How to Use",
    "📊 My Credits", "🛒 Buy Credits",
    "🎁 Daily Claim"
]

def is_authorized(user_id):
    return str(user_id) in ALLOWED_USERS

def get_user_credits(user_id):
    user_id = str(user_id)
    if user_id == YOUR_CHAT_ID:
        return "UNLIMITED"
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {"credits": 5, "last_claim": 0}
    return USER_DATA[user_id]["credits"]

# --- KEYBOARDS ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Top Priority (ACTIVE APIs)
    markup.row(BTN_NUM)
    markup.row(BTN_AADHAAR)
    
    # Divider for upcoming features
    markup.row("🔹 PREMIUM FEATURES (SOON) 🔹")
    
    # Coming Soon Buttons
    markup.row("⏳ [SOON] 🧠 TG ID → Num", "⏳ [SOON] 👤 TG User → Num")
    markup.row("⏳ [SOON] 👥 Aadhaar Family", "⏳ [SOON] 📧 Email → Num")
    markup.row("⏳ [SOON] 🌐 Web Scraper", "⏳ [SOON] 🚗 Vehicle → Num")
    markup.row("⏳ [SOON] 🏡 Vehicle Address", "⏳ [SOON] 📄 RC → PDF")
    markup.row("⏳ [SOON] 🚨 Vehicle Challan", "⏳ [SOON] 📸 Instagram Info")
    markup.row("⏳ [SOON] 📝 Name → Random Info", "⏳ [SOON] 🆔 Aadhaar → Ration")
    markup.row("⏳ [SOON] 💳 PAN Info", "⏳ [SOON] ⚪ LPG Info")
    markup.row("⏳ [SOON] 🚙 Num → Vehicle", "⏳ [SOON] 🎮 BGMI Info")
    
    # Info & Account Buttons
    markup.row("✨ Features", "📖 How to Use")
    markup.row("📊 My Credits", "🛒 Buy Credits")
    markup.row("🎁 Daily Claim")
    
    return markup

def result_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_dev = types.InlineKeyboardButton("👨‍💻 Contact Developer (NERD)", url=f"tg://user?id={YOUR_CHAT_ID}")
    markup.add(btn_dev)
    return markup

# Aesthetic Terminal Line
LINE = "✦⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯✦"

# --- ACCESS DENIED ---
def send_access_denied(message):
    text = (
        "<pre>"
        f"{LINE}\n"
        "❌ ACCESS DENIED\n"
        f"{LINE}\n"
        "STATUS  : RESTRICTED\n"
        "REASON  : INSUFFICIENT CLEARANCE\n"
        "CREDITS : 0\n\n"
        "This is a private NERD OSINT tool.\n"
        "You don't have permission to use it.\n"
        f"{LINE}\n"
        "👉 To get VIP access and credits,\n"
        "contact NERD via the button below.\n"
        f"{LINE}"
        "</pre>"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=result_menu())

# --- AUTO DELETE ---
def delete_message_later(chat_id, message_id, delay=60):
    time.sleep(delay)
    try:
        bot.delete_message(chat_id, message_id)
    except Exception:
        pass

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    first_name = message.from_user.first_name
    credits = get_user_credits(user_id)
    
    image_url = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
    
    profile_text = (
        "<pre>"
        "╔══════════════════════════════╗\n"
        "║      NERD PRIVATE OSINT      ║\n"
        "╚══════════════════════════════╝\n"
        "👋 Welcome!\n"
        f"{LINE}\n"
        f"👤 NAME    : {first_name}\n"
        f"🆔 USER ID : {user_id}\n"
        f"💳 CREDITS : {credits}\n"
        f"{LINE}\n"
        "✨ WHAT CAN THIS BOT DO?\n"
        "🔍 OSINT INTELLIGENCE\n"
        "🌐 Open Source Intelligence\n"
        "📱 Number • Username • Domain\n"
        "📊 Data Discovery • Verification\n"
        "⚡ Fast • Smart • Reliable\n"
        f"{LINE}\n"
        "🚧 NOTE: ONLY 2 APIs ARE ACTIVE.\n"
        "✅ [LIVE] Indian Number & Aadhaar Info.\n"
        "⏳ [SOON] Other services coming soon!\n"
        f"{LINE}\n"
        "🔒 VIP Access required for searching.\n"
        "👑 OWNER — @OSMIUM_9\n"
        "🛡 Privacy • Responsible OSINT\n"
        "⚠️ Only for lawful research & verified use.\n"
        f"{LINE}"
        "</pre>"
    )

    bot.send_photo(message.chat.id, image_url, caption=profile_text, parse_mode='HTML', reply_markup=main_menu())

# --- HOW TO USE ---
@bot.message_handler(func=lambda message: message.text == "📖 How to Use")
def how_to_use(message):
    text = (
        "<pre>"
        "📖 SYSTEM MANUAL\n"
        f"{LINE}\n"
        "[1] Select a feature from the menu.\n"
        "[2] Send the required information.\n"
        "[3] Cost: 1 credit per search.\n"
        "[4] Use 'Daily Claim' for free credits.\n"
        "[5] Reports auto-delete in 60s.\n"
        f"{LINE}\n"
        "SUPPORT: @OSMIUM_9"
        "</pre>"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())

# --- FEATURES LIST ---
@bot.message_handler(func=lambda message: message.text == "✨ Features")
def features_list(message):
    text = (
        "<pre>"
        "✨ ALL FEATURES ✨\n"
        f"{LINE}\n"
        "✅ [LIVE] 📱 NUM LOOKUP\n"
        "✅ [LIVE] 🆔 AADHAAR INFO\n"
        "⏳ [SOON] 🧠 TG ID → Num\n"
        "⏳ [SOON] 👤 TG User → Num\n"
        "⏳ [SOON] 👥 Aadhaar Family\n"
        "⏳ [SOON] 📧 Email → Num\n"
        "⏳ [SOON] 🌐 Web Scraper\n"
        "⏳ [SOON] 🚗 Vehicle → Num\n"
        "⏳ [SOON] 🏡 Vehicle Address\n"
        "⏳ [SOON] 📄 RC → PDF\n"
        "⏳ [SOON] 🚨 Vehicle Challan\n"
        "⏳ [SOON] 📸 Instagram Info\n"
        "⏳ [SOON] 📝 Name → Random Info\n"
        "⏳ [SOON] 🆔 Aadhaar → Ration\n"
        "⏳ [SOON] 💳 PAN Info\n"
        "⏳ [SOON] ⚪ LPG Info\n"
        "⏳ [SOON] 🚙 Num → Vehicle\n"
        "⏳ [SOON] 🎮 BGMI Info\n"
        f"{LINE}\n"
        "👑 Contact @OSMIUM_9"
        "</pre>"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())

# --- BUY CREDITS ---
@bot.message_handler(func=lambda message: message.text == "🛒 Buy Credits")
def buy_credits(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    text = (
        "<pre>"
        "🛒 BUY CREDITS\n"
        f"{LINE}\n"
        "Status : AVAILABLE\n"
        "Method : Manual Contact\n\n"
        "To purchase more credits, please contact\n"
        "the developer directly.\n"
        f"{LINE}\n"
        "👉 Click the button below to message NERD."
        "</pre>"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=result_menu())

# --- DAILY CLAIM ---
@bot.message_handler(func=lambda message: message.text == "🎁 Daily Claim")
def daily_claim(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
        
    user_id = str(message.from_user.id)
    if user_id == YOUR_CHAT_ID:
        bot.reply_to(message, "<pre>👑 OWNER: UNLIMITED CREDITS</pre>", parse_mode='HTML', reply_markup=main_menu())
        return

    if user_id not in USER_DATA:
        USER_DATA[user_id] = {"credits": 0, "last_claim": 0}

    current_time = time.time()
    last_claim = USER_DATA[user_id]["last_claim"]
    
    if current_time - last_claim < 86400:
        remaining = 86400 - (current_time - last_claim)
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        text = (
            "<pre>"
            "⏳ CLAIM BLOCKED\n"
            f"{LINE}\n"
            "You have already claimed today.\n"
            f"TIME LEFT : {hours}h {minutes}m\n"
            f"{LINE}"
            "</pre>"
        )
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())
        return
        
    USER_DATA[user_id]["credits"] += 10
    USER_DATA[user_id]["last_claim"] = current_time
    text = (
        "<pre>"
        "🎉 CLAIM SUCCESSFUL\n"
        f"{LINE}\n"
        "+10 CREDITS ADDED\n"
        f"BALANCE : {USER_DATA[user_id]['credits']}\n"
        f"{LINE}"
        "</pre>"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())

# --- CHECK CREDITS ---
@bot.message_handler(func=lambda message: message.text == "📊 My Credits")
def check_credits(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    credits = get_user_credits(message.from_user.id)
    text = (
        "<pre>"
        "💳 BALANCE INQUIRY\n"
        f"{LINE}\n"
        f"USER ID : {message.from_user.id}\n"
        f"CREDITS : {credits}\n"
        f"{LINE}\n"
        "Contact NERD to buy more."
        "</pre>"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())

# --- WORKING API PROMPTS ---
@bot.message_handler(func=lambda message: message.text == BTN_NUM)
def prompt_mobile(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    text = (
        "<pre>"
        "📱 MOBILE SEARCH INITIATED\n"
        f"{LINE}\n"
        "Please type a 10-digit Mobile Number below:"
        "</pre>"
    )
    msg = bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())
    bot.register_next_step_handler(msg, process_search, "MOBILE")

@bot.message_handler(func=lambda message: message.text == BTN_AADHAAR)
def prompt_aadhaar(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    text = (
        "<pre>"
        "🆔 AADHAAR SEARCH INITIATED\n"
        f"{LINE}\n"
        "Please type a 12-digit Aadhaar Number below:"
        "</pre>"
    )
    msg = bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())
    bot.register_next_step_handler(msg, process_search, "AADHAAR")

# --- "COMING SOON" HANDLER ---
@bot.message_handler(func=lambda message: message.text.startswith("⏳"))
def coming_soon(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
        
    feature_name = message.text.replace("⏳ [SOON]", "").strip()
    text = (
        "<pre>"
        "⚠️ SYSTEM UPDATE IN PROGRESS\n"
        f"{LINE}\n"
        f"FEATURE : {feature_name}\n"
        "STATUS  : PENDING DEPLOYMENT\n"
        "ETA     : SOON\n"
        f"{LINE}\n"
        "Contact @OSMIUM_9 for early access."
        "</pre>"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())

# --- MAIN SEARCH FUNCTION ---
def process_search(message, query_type, direct_query=None):
    user_id = str(message.from_user.id)
    if not is_authorized(user_id):
        return send_access_denied(message)

    query = direct_query if direct_query else message.text.strip()
    
    # 🛑 MENU BUG FIX
    if query in ALL_MENU_BUTTONS:
        bot.clear_step_handler(message)
        if query == BTN_NUM: prompt_mobile(message)
        elif query == BTN_AADHAAR: prompt_aadhaar(message)
        elif query == "📖 How to Use": how_to_use(message)
        elif query == "✨ Features": features_list(message)
        elif query == "📊 My Credits": check_credits(message)
        elif query == "🛒 Buy Credits": buy_credits(message)
        elif query == "🎁 Daily Claim": daily_claim(message)
        elif query.startswith("⏳"): coming_soon(message)
        return
        
    # Validation
    if query_type == "MOBILE" and (not query.isdigit() or len(query) != 10):
        bot.reply_to(message, "<pre>❌ ERROR: Invalid Mobile Number.\nPlease enter exactly 10 digits.</pre>", parse_mode='HTML', reply_markup=main_menu())
        return
    if query_type == "AADHAAR" and (not query.isdigit() or len(query) != 12):
        bot.reply_to(message, "<pre>❌ ERROR: Invalid Aadhaar Number.\nPlease enter exactly 12 digits.</pre>", parse_mode='HTML', reply_markup=main_menu())
        return

    # 💳 DEDUCT CREDITS
    if user_id != YOUR_CHAT_ID:
        if user_id not in USER_DATA:
            USER_DATA[user_id] = {"credits": 5, "last_claim": 0}
        if USER_DATA[user_id]["credits"] < 1:
            bot.reply_to(message, "<pre>❌ ERROR: INSUFFICIENT CREDITS.\nYou need 1 credit to search.</pre>", parse_mode='HTML', reply_markup=main_menu())
            return
        USER_DATA[user_id]["credits"] -= 1

    # 🔥 SAVE HISTORY
    if user_id not in SEARCH_HISTORY:
        SEARCH_HISTORY[user_id] = []
    SEARCH_HISTORY[user_id].append(query)

    if query in PROTECTED_NUMBERS:
        bot.reply_to(message, "<pre>🚫 ERROR: PROTECTED IDENTITY.\nAccess Denied.</pre>", parse_mode='HTML', reply_markup=main_menu())
        return
        
    msg = bot.send_message(message.chat.id, f"<pre>⚡ SEARCHING {query_type}:\n{LINE}\nTARGET: {query}\n<code>[■□□□□□□□□□] INITIALIZING...</code></pre>", parse_mode='HTML')
    
    for stage in ["> [■■■□□□□□□□] BYPASSING FIREWALLS...", "> [■■■■■■■■□□] EXTRACTING RECORDS..."]:
        time.sleep(0.5)
        bot.edit_message_text(f"<pre>⚡ SEARCHING:\n{LINE}\nTARGET: {query}\n<code>{stage}</code></pre>", message.chat.id, msg.message_id, parse_mode='HTML')
        
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

        curr_cred = "UNLIMITED" if user_id == YOUR_CHAT_ID else USER_DATA[user_id]["credits"]

        report = (
            "<pre>"
            "NERD PRIVATE OSINT REPORT\n"
            f"{LINE}\n"
            f"QUERY       : {query}\n"
            f"TYPE        : {query_type}\n"
            "------------------------------\n"
            f"NAME        : {name}\n"
            f"FATHER NAME : {fname}\n"
            f"MOBILE      : {mobile}\n"
            f"ALT NUMBER  : {alt}\n"
            f"AADHAAR NO  : {aadhaar}\n"
            f"ADDRESS     : {clean_address}\n"
            "------------------------------\n"
            f"CREDITS LEFT: {curr_cred}\n"
            "BY          : @OSMIUM_9\n"
            f"{LINE}\n"
            "⚠️ THIS REPORT WILL DELETE IN 60 SECONDS.\n"
            "SAVE THIS DATA.\n"
            "</pre>"
        )
        
        sent_msg = bot.edit_message_text(report, message.chat.id, msg.message_id, parse_mode='HTML', reply_markup=result_menu())
        threading.Thread(target=delete_message_later, args=(message.chat.id, sent_msg.message_id, 60)).start()
        
    else:
        sent_msg = bot.edit_message_text(
            text=f"<pre>🔴 DATA NOT FOUND\n{LINE}\nTARGET : {query}\nSTATUS : NO RECORDS FOUND.</pre>",
            chat_id=message.chat.id, message_id=msg.message_id, parse_mode='HTML', reply_markup=result_menu()
        )
        threading.Thread(target=delete_message_later, args=(message.chat.id, sent_msg.message_id, 60)).start()

# --- INVALID INPUT HANDLER ---
@bot.message_handler(func=lambda message: True)
def invalid_input(message):
    if not is_authorized(message.from_user.id): 
        return send_access_denied(message)
    bot.reply_to(message, "<pre>❌ ERROR: Unrecognized Command.\nPlease use the menu below.</pre>", parse_mode='HTML', reply_markup=main_menu())

# --- WEB SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "NERD PRIVATE OSINT Bot is running!"
def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    print("🤖 NERD PRIVATE OSINT is running...")
    bot.polling(none_stop=True)
