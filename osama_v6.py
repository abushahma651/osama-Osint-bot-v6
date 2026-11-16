from flask import Flask
import threading
import os
import telebot
import requests
import time
import json
import random
import string
from telebot import types

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
YOUR_CHAT_ID = str(os.environ.get('CHAT_ID'))
API_BASE_URL = "https://api.darknetwork.site/index.php?api=hi_tek&key=key_DarkApiX444&search={}"

bot = telebot.TeleBot(BOT_TOKEN)

# --- DATABASE ---
USER_DATA = {} 
SEARCH_HISTORY = {} 
REDEEM_CODES = {} 
PROTECTED_NUMBERS = ["9621303160", "7991536322", "8604302624", "6204473620"]

ALLOWED_USERS = [
    YOUR_CHAT_ID,       
    "8707785706", "8898567917", "6700078527",
    "5704555109", "901112667", "8659201578"
]

BTN_NUM = "✅ [LIVE] 📱 NUM LOOKUP"
BTN_AADHAAR = "✅ [LIVE] 🆔 AADHAAR INFO"

def is_authorized(user_id):
    return str(user_id) in ALLOWED_USERS

def get_user_credits(user_id):
    user_id = str(user_id)
    if user_id == YOUR_CHAT_ID:
        return "UNLIMITED"
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {"credits": 5, "last_claim": 0}
    return USER_DATA[user_id]["credits"]

def generate_code(length=8):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# --- KEYBOARDS ---
def main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(BTN_NUM)
    markup.row(BTN_AADHAAR)
    markup.row("🎟️ Redeem Code")
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
    
    # 👑 ADMIN PANEL BUTTON (Only for Owner)
    if str(user_id) == YOUR_CHAT_ID:
        markup.row("👑 ADMIN PANEL")
        
    return markup

# Admin Panel Inline Keyboard
def admin_panel_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_list = types.InlineKeyboardButton("📋 List Users", callback_data="adm_list")
    btn_history = types.InlineKeyboardButton("📊 History", callback_data="adm_history")
    btn_broadcast = types.InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast")
    btn_addcredit = types.InlineKeyboardButton("➕ Add Credits", callback_data="adm_addcredit")
    btn_gencode = types.InlineKeyboardButton("🎟️ Gen Code", callback_data="adm_gencode")
    btn_allow = types.InlineKeyboardButton("✅ Allow User", callback_data="adm_allow")
    btn_remove = types.InlineKeyboardButton("❌ Remove User", callback_data="adm_remove")
    btn_close = types.InlineKeyboardButton("🔙 Close Panel", callback_data="adm_close")
    
    markup.add(btn_list, btn_history)
    markup.add(btn_broadcast, btn_addcredit)
    markup.add(btn_gencode, btn_allow)
    markup.add(btn_remove, btn_close)
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
# 👑 ADMIN PANEL LOGIC
# =====================================================================

@bot.message_handler(func=lambda message: message.text == "👑 ADMIN PANEL" and str(message.from_user.id) == YOUR_CHAT_ID)
def show_admin_panel(message):
    text = f"<pre>👑 OWNER CONTROL PANEL\n{LINE}\nSelect an action below:</pre>"
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=admin_panel_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_") and str(call.from_user.id) == YOUR_CHAT_ID)
def admin_callbacks(call):
    action = call.data.split("_")[1]
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    
    if action == "close":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "<pre>Admin Panel Closed.</pre>", parse_mode='HTML', reply_markup=main_menu(call.from_user.id))
        
    elif action == "list":
        text = "<pre>👑 VIP ACCESS LIST\n" + LINE + "\n"
        for i, uid in enumerate(ALLOWED_USERS, 1):
            role = "(OWNER)" if str(uid) == YOUR_CHAT_ID else ""
            try:
                name = bot.get_chat(uid).first_name
            except:
                name = "Unknown"
            text += f"{i}. {name} | {uid} {role}\n"
        text += LINE + "</pre>"
        bot.send_message(call.message.chat.id, text, parse_mode='HTML')
        
    elif action == "history":
        if not SEARCH_HISTORY:
            bot.send_message(call.message.chat.id, "<pre>📊 No search history found.</pre>", parse_mode='HTML')
            return
        text = "<pre>📊 FULL SEARCH HISTORY\n" + LINE + "\n"
        for uid, queries in SEARCH_HISTORY.items():
            text += f"👤 ID : {uid}\n"
            text += f"🔍 Total : {len(queries)}\n"
            text += "------------------------------\n"
        text += "</pre>"
        if len(text) > 4000:
            with open("history.txt", "w") as f:
                f.write(text)
            bot.send_document(call.message.chat.id, open("history.txt", "rb"))
        else:
            bot.send_message(call.message.chat.id, text, parse_mode='HTML')
            
    elif action == "broadcast":
        msg = bot.send_message(call.message.chat.id, "<pre>📢 Enter the broadcast message:</pre>", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_broadcast)
        
    elif action == "addcredit":
        msg = bot.send_message(call.message.chat.id, "<pre>➕ Enter User ID and Amount\nFormat: 123456789 50</pre>", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_addcredit)
        
    elif action == "gencode":
        msg = bot.send_message(call.message.chat.id, "<pre>🎟️ Enter amount for new code (e.g., 50):</pre>", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_gencode)
        
    elif action == "allow":
        msg = bot.send_message(call.message.chat.id, "<pre>✅ Enter User ID to allow:</pre>", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_allow)
        
    elif action == "remove":
        msg = bot.send_message(call.message.chat.id, "<pre>❌ Enter User ID to remove:</pre>", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_remove)

# --- ADMIN PROCESSING FUNCTIONS ---

def process_broadcast(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    msg_text = message.text
    success = 0
    for uid in ALLOWED_USERS:
        try:
            bot.send_message(uid, f"<pre>📢 ADMIN BROADCAST\n{LINE}\n{msg_text}\n{LINE}</pre>", parse_mode='HTML')
            success += 1
        except: pass
    bot.reply_to(message, f"<pre>✅ Broadcast sent to {success} users.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

def process_addcredit(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    try:
        args = message.text.split()
        target_id, amount = args[0], int(args[1])
        if target_id not in USER_DATA: USER_DATA[target_id] = {"credits": 0, "last_claim": 0}
        USER_DATA[target_id]["credits"] += amount
        bot.reply_to(message, f"<pre>✅ Added {amount} credits to {target_id}.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))
        try: bot.send_message(target_id, f"<pre>🎉 You received {amount} credits from Admin!</pre>", parse_mode='HTML')
        except: pass
    except:
        bot.reply_to(message, "<pre>❌ Invalid format. Use: 123456789 50</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

def process_gencode(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    try:
        amount = int(message.text)
        code = generate_code()
        REDEEM_CODES[code] = amount
        bot.reply_to(message, f"<pre>🎟️ CODE: {code}\nVALUE: {amount} Credits</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))
    except:
        bot.reply_to(message, "<pre>❌ Invalid amount.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

def process_allow(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    new_id = message.text.strip()
    if new_id not in ALLOWED_USERS:
        ALLOWED_USERS.append(new_id)
        bot.reply_to(message, f"<pre>✅ User {new_id} allowed.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))
    else:
        bot.reply_to(message, "<pre>⚠️ User already allowed.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

def process_remove(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    rem_id = message.text.strip()
    if rem_id in ALLOWED_USERS and rem_id != YOUR_CHAT_ID:
        ALLOWED_USERS.remove(rem_id)
        bot.reply_to(message, f"<pre>✅ User {rem_id} removed.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))
    else:
        bot.reply_to(message, "<pre>⚠️ User not found or cannot remove Owner.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

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
    bot.send_photo(message.chat.id, image_url, caption=profile_text, parse_mode='HTML', reply_markup=main_menu(user_id))

@bot.message_handler(commands=['redeem'])
def redeem_code(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    user_id = str(message.from_user.id)
    try:
        code = message.text.split()[1].upper()
        if code in REDEEM_CODES:
            amount = REDEEM_CODES[code]
            if user_id not in USER_DATA: USER_DATA[user_id] = {"credits": 0, "last_claim": 0}
            USER_DATA[user_id]["credits"] += amount
            del REDEEM_CODES[code]
            bot.reply_to(message, f"<pre>🎉 CODE REDEEMED\n{LINE}\n+{amount} CREDITS\nBALANCE : {USER_DATA[user_id]['credits']}\n{LINE}</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
        else:
            bot.reply_to(message, "<pre>❌ Invalid or Expired Code.</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
    except IndexError:
        bot.reply_to(message, "<pre>❌ Usage: /redeem YOUR_CODE</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))

@bot.message_handler(func=lambda message: message.text == "🎟️ Redeem Code")
def prompt_redeem(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    msg = bot.reply_to(message, "<pre>🎟️ ENTER REDEEM CODE\n" + LINE + "\nType your code below:</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))
    
    def process_redeem(msg):
        if msg.text.startswith('/') or msg.text in ["👑 ADMIN PANEL"]: 
            bot.clear_step_handler(msg)
            return
            
        user_id = str(msg.from_user.id)
        code = msg.text.strip().upper()
        if code in REDEEM_CODES:
            amount = REDEEM_CODES[code]
            if user_id not in USER_DATA: USER_DATA[user_id] = {"credits": 0, "last_claim": 0}
            USER_DATA[user_id]["credits"] += amount
            del REDEEM_CODES[code]
            bot.reply_to(msg, f"<pre>🎉 CODE REDEEMED\n{LINE}\n+{amount} CREDITS\nBALANCE : {USER_DATA[user_id]['credits']}\n{LINE}</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
        else:
            bot.reply_to(msg, "<pre>❌ Invalid or Expired Code.</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
    bot.register_next_step_handler(msg, process_redeem)

@bot.message_handler(func=lambda message: message.text == "📖 How to Use")
def how_to_use(message):
    text = (
        "<pre>"
        "📖 SYSTEM MANUAL\n"
        f"{LINE}\n"
        "[1] Select a feature from the menu.\n"
        "[2] Send the required information.\n"
        "[3] Cost: 1 credit per successful search.\n"
        "[4] Use 'Daily Claim' for free credits.\n"
        "[5] Use 'Redeem Code' for bonus credits.\n"
        "[6] Reports auto-delete in 60s.\n"
        f"{LINE}\n"
        "SUPPORT: @OSMIUM_9"
        "</pre>"
    )
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

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
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

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
        bot.reply_to(message, "<pre>👑 OWNER: UNLIMITED CREDITS</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
        return

    if user_id not in USER_DATA:
        USER_DATA[user_id] = {"credits": 0, "last_claim": 0}

    current_time = time.time()
    last_claim = USER_DATA[user_id]["last_claim"]
    
    if current_time - last_claim < 86400:
        remaining = 86400 - (current_time - last_claim)
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        text = f"<pre>⏳ CLAIM BLOCKED\n{LINE}\nTIME LEFT : {hours}h {minutes}m\n{LINE}</pre>"
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(user_id))
        return
        
    USER_DATA[user_id]["credits"] += 10
    USER_DATA[user_id]["last_claim"] = current_time
    text = f"<pre>🎉 CLAIM SUCCESSFUL\n{LINE}\n+10 CREDITS ADDED\nBALANCE : {USER_DATA[user_id]['credits']}\n{LINE}</pre>"
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(user_id))

@bot.message_handler(func=lambda message: message.text == "📊 My Credits")
def check_credits(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    credits = get_user_credits(message.from_user.id)
    text = f"<pre>💳 BALANCE INQUIRY\n{LINE}\nUSER ID : {message.from_user.id}\nCREDITS : {credits}\n{LINE}\n</pre>"
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

@bot.message_handler(func=lambda message: message.text == BTN_NUM)
def prompt_mobile(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    text = f"<pre>📱 MOBILE SEARCH INITIATED\n{LINE}\nType a 10-digit Mobile Number:</pre>"
    msg = bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(message.from_user.id))
    bot.register_next_step_handler(msg, process_search, "MOBILE")

@bot.message_handler(func=lambda message: message.text == BTN_AADHAAR)
def prompt_aadhaar(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    text = f"<pre>🆔 AADHAAR SEARCH INITIATED\n{LINE}\nType a 12-digit Aadhaar Number:</pre>"
    msg = bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(message.from_user.id))
    bot.register_next_step_handler(msg, process_search, "AADHAAR")

@bot.message_handler(func=lambda message: message.text.startswith("⏳"))
def coming_soon(message):
    if not is_authorized(message.from_user.id):
        return send_access_denied(message)
    feature_name = message.text.replace("⏳ [SOON]", "").strip()
    text = f"<pre>⚠️ SERVICE UNAVAILABLE\n{LINE}\nFEATURE : {feature_name}\nSTATUS  : COMING SOON\n{LINE}</pre>"
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

# --- MAIN SEARCH FUNCTION ---
def process_search(message, query_type, direct_query=None):
    user_id = str(message.from_user.id)
    if not is_authorized(user_id):
        return send_access_denied(message)

    query = direct_query if direct_query else message.text.strip()
    
    if query.startswith("⏳") or query == "👑 ADMIN PANEL" or query in [BTN_NUM, BTN_AADHAAR, "📖 How to Use", "✨ Features", "📊 My Credits", "🛒 Buy Credits", "🎁 Daily Claim", "🎟️ Redeem Code"]:
        bot.clear_step_handler(message)
        return
        
    if query_type == "MOBILE" and (not query.isdigit() or len(query) != 10):
        bot.reply_to(message, "<pre>❌ ERROR: Invalid Mobile Number.\nPlease enter exactly 10 digits.</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
        return
    if query_type == "AADHAAR" and (not query.isdigit() or len(query) != 12):
        bot.reply_to(message, "<pre>❌ ERROR: Invalid Aadhaar Number.\nPlease enter exact
