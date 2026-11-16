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
    markup.row(BTN_NUM)
    markup.row(BTN_AADHAAR)
    markup.row("🔹 PREMIUM FEATURES (SOON) 🔹")
    markup.row("⏳ [SOON] 🧠 TG ID → Num", "⏳ [SOON] 👤 TG User → Num")
    markup.row("⏳ [SOON] 👥 Aadhaar Family", "⏳ [SOON] 📧 Email → Num")
    markup.row("⏳ [SOON] 🌐 Web Scraper", "⏳ [SOON] 🚗 Vehicle → Num")
    markup.row("⏳ [SOON] 🏡 Vehicle Address", "⏳ [SOON] 📄 RC → PDF")
    markup.row("⏳ [SOON] 🚨 Vehicle Challan", "⏳ [SOON] 📸 Instagram Info")
    markup.row("⏳ [SOON] 📝 Name → Random Info", "⏳ [SOON] 🆔 Aadhaar → Ration")
    markup.row("⏳ [SOON] 💳 PAN Info", "⏳ [SOON] ⚪ LPG Info")
    markup.row("⏳ [SOON] 🚙 Num → Vehicle", "⏳ [SOON] 🎮 BGMI Info")
    markup.row("✨ Features", "📖 How to Use")
    markup.row("📊 My Credits", "🛒 Buy Credits")
    markup.row("🎁 Daily Claim")
    return markup

def result_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_dev = types.InlineKeyboardButton("👨‍💻 Contact Developer (NERD)", url=f"tg://user?id={YOUR_CHAT_ID}")
    markup.add(btn_dev)
    return markup

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

# =====================================================================
# 👑 ADMIN COMMANDS (OWNER ONLY)
# =====================================================================

@bot.message_handler(commands=['allow'])
def admin_allow(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    try:
        new_id = message.text.split()[1]
        if new_id not in ALLOWED_USERS:
            ALLOWED_USERS.append(new_id)
            text = f"<pre>✅ ACCESS GRANTED\n{LINE}\nUser ID : {new_id}\nStatus  : VIP MEMBER\n{LINE}</pre>"
            bot.reply_to(message, text, parse_mode='HTML')
        else:
            bot.reply_to(message, "<pre>⚠️ User is already in VIP list.</pre>", parse_mode='HTML')
    except IndexError:
        bot.reply_to(message, "<pre>❌ Format: /allow 123456789</pre>", parse_mode='HTML')

@bot.message_handler(commands=['remove'])
def admin_remove(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    try:
        rem_id = message.text.split()[1]
        if rem_id in ALLOWED_USERS and rem_id != YOUR_CHAT_ID:
            ALLOWED_USERS.remove(rem_id)
            text = f"<pre>✅ ACCESS REVOKED\n{LINE}\nUser ID : {rem_id}\nStatus  : REMOVED\n{LINE}</pre>"
            bot.reply_to(message, text, parse_mode='HTML')
        else:
            bot.reply_to(message, "<pre>⚠️ User not found or cannot remove Owner.</pre>", parse_mode='HTML')
    except IndexError:
        bot.reply_to(message, "<pre>❌ Format: /remove 123456789</pre>", parse_mode='HTML')

@bot.message_handler(commands=['list_users'])
def admin_list(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    
    text = "<pre>👑 VIP ACCESS LIST\n" + LINE + "\n"
    for i, uid in enumerate(ALLOWED_USERS, 1):
        role = "(OWNER)" if str(uid) == YOUR_CHAT_ID else ""
        try:
            name = bot.get_chat(uid).first_name
        except:
            name = "Unknown"
        text += f"{i}. {name} | {uid} {role}\n"
    text += LINE + "</pre>"
    
    bot.reply_to(message, text, parse_mode='HTML')

@bot.message_handler(commands=['history'])
def admin_history(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    
    if not SEARCH_HISTORY:
        bot.reply_to(message, "<pre>📊 No search history found.</pre>", parse_mode='HTML')
        return
        
    text = "<pre>📊 FULL SEARCH HISTORY\n" + LINE + "\n"
    for uid, queries in SEARCH_HISTORY.items():
        text += f"👤 User ID : {uid}\n"
        text += f"🔍 Queries : {', '.join(queries)}\n"
        text += f"📈 Total   : {len(queries)}\n"
        text += "------------------------------\n"
    text += "</pre>"
    
    if len(text) > 4000:
        with open("history.txt", "w") as f:
            f.write(text)
        bot.send_document(message.chat.id, open("history.txt", "rb"), caption="Full History File")
    else:
        bot.reply_to(message, text, parse_mode='HTML')

@bot.message_handler(commands=['broadcast'])
def admin_broadcast(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    
    msg_text = message.text.replace("/broadcast", "").strip()
    if not msg_text:
        bot.reply_to(message, "<pre>❌ Usage: /broadcast Your message here</pre>", parse_mode='HTML')
        return
        
    success_count = 0
    for uid in ALLOWED_USERS:
        try:
            broadcast_format = f"<pre>📢 ADMIN BROADCAST\n{LINE}\n{msg_text}\n{LINE}</pre>"
            bot.send_message(uid, broadcast_format, parse_mode='HTML')
            success_count += 1
        except Exception:
            pass
            
    bot.reply_to(message, f"<pre>✅ Broadcast sent successfully to {success_count} users.</pre>", parse_mode='HTML')

# =====================================================================
# 🤖 PUBLIC COMMANDS
# =====================================================================

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
        "📱 Number • Username • Domain\n"
        "📊 Data Discovery • Verification\n"
        f"{LINE}\n"
        "🚧 NOTE: ONLY 2 APIs ARE ACTIVE.\n"
        "✅ [LIVE] Indian Number & Aadhaar Info.\n"
        "⏳ [SOON] Other services coming soon!\n"
        f"{LINE}\n"
        "🔒 VIP Access required for searching.\n"
        "👑 OWNER — @OSMIUM_9\n"
        f"{LINE}"
        "</pre>"
    )
    bot.send_photo(message.chat.id, image_url, caption=profile_text, parse_mode='HTML', reply_markup=main_menu())

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

@bot.message_handler(func=lambda message: message.text == "✨ Features")
def features_list(message):
    text = (
        "<pre>"
        "✨ ALL FEATURES ✨\n"
        f"{LINE}\n"
        "✅ [LIVE] 📱 NUM LOOKUP\n"
        "✅ [LIVE] 🆔 AADHAAR INFO\n"
        "⏳ [SOON] 🧠 TG ID → Num\n"
        "⏳ [SOON] 🚗 Vehicle → Num\n"
        "⏳ [SOON] 💳 PAN Info\n"
        "⏳ [SOON] 🆔 Aadhaar → Ration\n"
        f"{LINE}\n"
        "👑 Contact @OSMIUM_9"
        "</pre>"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "🛒 Buy Credits")
def buy_credits(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    text = (
        "<pre>"
        "🛒 BUY CREDITS\n"
        f"{LINE}\n"
        "Status : AVAILABLE\n"
        "Method : Manual Contact\n"
        f"{LINE}\n"
        "👉 Click the button below to message NERD."
        "</pre>"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=result_menu())

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
        "</pre>"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == BTN_NUM)
def prompt_mobile(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    text = f"<pre>📱 MOBILE SEARCH INITIATED\n{LINE}\nType a 10-digit Mobile Number:</pre>"
    msg = bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())
    bot.register_next_step_handler(msg, process_search, "MOBILE")

@bot.message_handler(func=lambda message: message.text == BTN_AADHAAR)
def prompt_aadhaar(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    text = f"<pre>🆔 AADHAAR SEARCH INITIATED\n{LINE}\nType a 12-digit Aadhaar Number:</pre>"
    msg = bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu())
    bot.register_next_step_handler(msg, process_search, "AADHAAR")

@bot.message_handler(func=lambda message: message.text.startswith("⏳"))
def coming_soon(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    feature_name = message.text.replace("⏳ [SOON]", "").strip()
    text = f"<pre>⚠️ SERVICE UNAVAILABLE\n{LINE}\nFEATURE : {feature_name}\nSTATUS  : COMING SOON\n{LINE}</pre>"
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
        
    if query_type == "MOBILE" and (not query.isdigit() or len(query) != 10):
        bot.reply_to(message, "<pre>❌ ERROR: Invalid Mobile Number.\nPlease enter exactly 10 digits.</pre>", parse_mode='HTML', reply_markup=main_menu())
        return
    if query_type == "AADHAAR" and (not query.isdigit() or len(query) != 12):
        bot.reply_to(message, "<pre>❌ ERROR: Invalid Aadhaar Number.\nPlease enter exactly 12 digits.</pre>", parse_mode='HTML', reply_markup=main_menu())
        return

    if user_id != YOUR_CHAT_ID:
        if user_id not in USER_DATA:
            USER_DATA[user_id] = {"credits": 5, "last_claim": 0}
        if USER_DATA[user_id]["credits"] < 1:
            bot.reply_to(message, "<pre>❌ ERROR: INSUFFICIENT CREDITS.\nYou need 1 credit to search.</pre>", parse_mode='HTML', reply_markup=main_menu())
            return
        USER_DATA[user_id]["credits"] -= 1
        
        # 🔥 LIVE ADMIN ALERT
        try:
            username = message.from_user.username
            first_name = message.from_user.first_name
            log_text = (
                f"<pre>"
                f"🚨 NEW SEARCH DETECTED 🚨\n"
                f"{LINE}\n"
                f"👤 NAME     : {first_name}\n"
                f"🔗 USERNAME : @{username if username else 'None'}\n"
                f"🆔 USER ID  : {user_id}\n"
                f"📊 TYPE     : {query_type}\n"
                f"🔍 QUERY    : {query}\n"
                f"{LINE}\n"
                f"💳 CREDITS LEFT: {USER_DATA[user_id]['credits']}"
                f"</pre>"
            )
            bot.send_message(YOUR_CHAT_ID, log_text, parse_mode='HTML')
        except Exception:
            pass

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
    # Yeh line Telegram ko force karegi ki woh purane atke hue messages clear kare
    bot.remove_webhook() 
    
    threading.Thread(target=run_web).start()
    print("🤖 NERD PRIVATE OSINT is running...")
    bot.polling(none_stop=True)
