from flask import Flask
import threading
import os
import telebot
import requests
import time
import random
import string
import traceback
from telebot import types

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
YOUR_CHAT_ID = str(os.environ.get('CHAT_ID'))
API_BASE_URL = "https://api.darknetwork.site/index.php?api=hi_tek&key=key_DarkApiX444&search={}"

bot = telebot.TeleBot(BOT_TOKEN)

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
LINE = "✦⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯✦"

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
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for i in range(length))

# --- KEYBOARDS ---
def main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(BTN_NUM, BTN_AADHAAR)
    markup.row("🎟️ Redeem Code", "📖 How to Use")
    markup.row("📊 My Credits", "🛒 Buy Credits")
    markup.row("🎁 Daily Claim", "✨ Features")
    markup.row("🔹 PREMIUM FEATURES (SOON) 🔹")
    markup.row("⏳ [SOON] 🧠 TG ID → Num", "⏳ [SOON] 👤 TG User → Num")
    markup.row("⏳ [SOON] 👥 Aadhaar Family", "⏳ [SOON] 📧 Email → Num")
    markup.row("⏳ [SOON] 🌐 Web Scraper", "⏳ [SOON] 🚗 Vehicle → Num")
    markup.row("⏳ [SOON] 🏡 Vehicle Address", "⏳ [SOON] 📄 RC → PDF")
    markup.row("⏳ [SOON] 🚨 Vehicle Challan", "⏳ [SOON] 📸 Instagram Info")
    markup.row("⏳ [SOON] 📝 Name → Random Info", "⏳ [SOON] 🆔 Aadhaar → Ration")
    markup.row("⏳ [SOON] 💳 PAN Info", "⏳ [SOON] ⚪ LPG Info")
    markup.row("⏳ [SOON] 🚙 Num → Vehicle", "⏳ [SOON] 🎮 BGMI Info")
    
    if str(user_id) == YOUR_CHAT_ID:
        markup.row("👑 ADMIN PANEL")
    return markup

def admin_panel_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📋 List Users", callback_data="adm_list"),
        types.InlineKeyboardButton("📊 History", callback_data="adm_history"),
        types.InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast"),
        types.InlineKeyboardButton("➕ Add Credits", callback_data="adm_addcredit"),
        types.InlineKeyboardButton("🎟️ Gen Code", callback_data="adm_gencode"),
        types.InlineKeyboardButton("✅ Allow User", callback_data="adm_allow"),
        types.InlineKeyboardButton("❌ Remove User", callback_data="adm_remove"),
        types.InlineKeyboardButton("🔙 Close Panel", callback_data="adm_close")
    )
    return markup

def result_menu():
    markup = types.InlineKeyboardMarkup()
    btn_dev = types.InlineKeyboardButton("👨‍💻 Contact Developer (NERD)", url=f"tg://user?id={YOUR_CHAT_ID}")
    markup.add(btn_dev)
    return markup

def send_access_denied(message):
    text = f"<pre>{LINE}\n❌ ACCESS DENIED\n{LINE}\nSTATUS  : RESTRICTED\nREASON  : INSUFFICIENT CLEARANCE\n\nThis is a private NERD OSINT tool.\nYou don't have permission to use it.\n{LINE}\n👉 To get VIP access, contact NERD.\n{LINE}</pre>"
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=result_menu())

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
            try: name = bot.get_chat(uid).first_name
            except: name = "Unknown"
            text += f"{i}. {name} | {uid} {role}\n"
        text += LINE + "</pre>"
        bot.send_message(call.message.chat.id, text, parse_mode='HTML')
    elif action == "history":
        if not SEARCH_HISTORY:
            bot.send_message(call.message.chat.id, "<pre>📊 No search history found.</pre>", parse_mode='HTML')
            return
        text = "<pre>📊 FULL SEARCH HISTORY\n" + LINE + "\n"
        for uid, queries in SEARCH_HISTORY.items():
            text += f"👤 ID : {uid}\n🔍 Total : {len(queries)}\n{LINE}\n"
        text += "</pre>"
        if len(text) > 4000:
            with open("history.txt", "w") as f: f.write(text)
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

def process_broadcast(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    success = 0
    for uid in ALLOWED_USERS:
        try:
            bot.send_message(uid, f"<pre>📢 ADMIN BROADCAST\n{LINE}\n{message.text}\n{LINE}</pre>", parse_mode='HTML')
            success += 1
        except: pass
    bot.reply_to(message, f"<pre>✅ Broadcast sent to {success} users.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

def process_addcredit(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    try:
        args = message.text.split()
        target_id = args[0]
        amount = int(args[1])
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
    credits = get_user_credits(user_id)
    image_url = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
    
    text1 = f"<pre>╔══════════════════════════════╗\n║      NERD PRIVATE OSINT      ║\n╚══════════════════════════════╝\n"
    text2 = f"👋 Welcome!\n{LINE}\n👤 NAME    : {message.from_user.first_name}\n🆔 USER ID : {user_id}\n💳 CREDITS : {credits}\n"
    text3 = f"{LINE}\n✨ WHAT CAN THIS BOT DO?\n🔍 OSINT INTELLIGENCE\n📱 Number • Username • Domain\n📊 Data Discovery • Verification\n"
    text4 = f"{LINE}\n🚧 NOTE: ONLY 2 APIs ARE ACTIVE.\n✅ [LIVE] Indian Number & Aadhaar Info.\n⏳ [SOON] Other services coming soon!\n"
    text5 = f"{LINE}\n🔒 VIP Access required for searching.\n👑 OWNER — @OSMIUM_9\n{LINE}</pre>"
    
    profile_text = text1 + text2 + text3 + text4 + text5
    bot.send_photo(message.chat.id, image_url, caption=profile_text, parse_mode='HTML', reply_markup=main_menu(user_id))

@bot.message_handler(commands=['redeem'])
def redeem_code(message):
    if not is_authorized(message.from_user.id): return send_access_denied(message)
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
    if not is_authorized(message.from_user.id): return send_access_denied(message)
    msg = bot.reply_to(message, "<pre>🎟️ ENTER REDEEM CODE\n" + LINE + "\nType your code below:</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))
    
    def process_redeem(msg):
        if msg.text.startswith('/') or msg.text == "👑 ADMIN PANEL": 
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

@bot.message_handler(func=lambda message: message.text in ["📖 How to Use", "✨ Features", "🛒 Buy Credits", "🎁 Daily Claim", "📊 My Credits"])
def static_menus(message):
    if not is_authorized(message.from_user.id): return send_access_denied(message)
    user_id = str(message.from_user.id)
    
    if message.text == "📖 How to Use":
        text = f"<pre>📖 SYSTEM MANUAL\n{LINE}\n[1] Select a feature from the menu.\n[2] Send the required info.\n[3] Cost: 1 credit per success.\n[4] Use Daily Claim for free credits.\n[5] Reports auto-delete in 60s.\n{LINE}\nSUPPORT: @OSMIUM_9</pre>"
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(user_id))
    elif message.text == "✨ Features":
        text = f"<pre>✨ ALL FEATURES ✨\n{LINE}\n✅ [LIVE] 📱 NUM LOOKUP\n✅ [LIVE] 🆔 AADHAAR INFO\n⏳ [SOON] 🧠 TG ID → Num\n⏳ [SOON] 🚗 Vehicle → Num\n⏳ [SOON] 💳 PAN Info\n{LINE}\n👑 Contact @OSMIUM_9</pre>"
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(user_id))
    elif message.text == "🛒 Buy Credits":
        text = f"<pre>🛒 BUY CREDITS\n{LINE}\nStatus : AVAILABLE\nMethod : Manual Contact\n{LINE}\n👉 Click the button below to message NERD.</pre>"
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=result_menu())
    elif message.text == "🎁 Daily Claim":
        if user_id == YOUR_CHAT_ID:
            bot.reply_to(message, "<pre>👑 OWNER: UNLIMITED CREDITS</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
            return
        if user_id not in USER_DATA: USER_DATA[user_id] = {"credits": 0, "last_claim": 0}
        current_time = time.time()
        if current_time - USER_DATA[user_id]["last_claim"] < 86400:
            remaining = 86400 - (current_time - USER_DATA[user_id]["last_claim"])
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            text = f"<pre>⏳ CLAIM BLOCKED\n{LINE}\nTIME LEFT : {hours}h {minutes}m\n{LINE}</pre>"
            bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(user_id))
            return
        USER_DATA[user_id]["credits"] += 10
        USER_DATA[user_id]["last_claim"] = current_time
        text = f"<pre>🎉 CLAIM SUCCESSFUL\n{LINE}\n+10 CREDITS\nBALANCE : {USER_DATA[user_id]['credits']}\n{LINE}</pre>"
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(user_id))
    elif message.text == "📊 My Credits":
        credits = get_user_credits(user_id)
        text = f"<pre>💳 BALANCE INQUIRY\n{LINE}\nUSER ID : {user_id}\nCREDITS : {credits}\n{LINE}\n</pre>"
        bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(user_id))

@bot.message_handler(func=lambda message: message.text in [BTN_NUM, BTN_AADHAAR])
def prompt_search(message):
    if not is_authorized(message.from_user.id): return send_access_denied(message)
    user_id = str(message.from_user.id)
    if message.text == BTN_NUM:
        text = f"<pre>📱 MOBILE SEARCH\n{LINE}\nType a 10-digit Mobile Number:</pre>"
        bot.register_next_step_handler(bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(user_id)), process_search, "MOBILE")
    else:
        text = f"<pre>🆔 AADHAAR SEARCH\n{LINE}\nType a 12-digit Aadhaar Number:</pre>"
        bot.register_next_step_handler(bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(user_id)), process_search, "AADHAAR")

@bot.message_handler(func=lambda message: message.text.startswith("⏳"))
def coming_soon(message):
    if not is_authorized(message.from_user.id): return send_access_denied(message)
    feature_name = message.text.replace("⏳ [SOON]", "").strip()
    text = f"<pre>⚠️ SERVICE UNAVAILABLE\n{LINE}\nFEATURE : {feature_name}\nSTATUS  : COMING SOON\n{LINE}</pre>"
    bot.reply_to(message, text, parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

def process_search(message, query_type, direct_query=None):
    user_id = str(message.from_user.id)
    if not is_authorized(user_id): return send_access_denied(message)

    query = direct_query if direct_query else message.text.strip()
    
    if query.startswith("⏳") or query == "👑 ADMIN PANEL" or query in [BTN_NUM, BTN_AADHAAR, "📖 How to Use", "✨ Features", "📊 My Credits", "🛒 Buy Credits", "🎁 Daily Claim", "🎟️ Redeem Code"]:
        bot.clear_step_handler(message)
        return
        
    if query_type == "MOBILE":
        if not query.isdigit() or len(query) != 10:
            return bot.reply_to(message, "<pre>❌ ERROR: Invalid Mobile Number.\nEnter exactly 10 digits.</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
    elif query_type == "AADHAAR":
        if not query.isdigit() or len(query) != 12:
            return bot.reply_to(message, "<pre>❌ ERROR: Invalid Aadhaar Number.\nEnter exactly 12 digits.</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))

    if user_id != YOUR_CHAT_ID:
        if user_id not in USER_DATA: USER_DATA[user_id] = {"credits": 5, "last_claim": 0}
        if USER_DATA[user_id]["credits"] < 1:
            return bot.reply_to(message, "<pre>❌ ERROR: INSUFFICIENT CREDITS.\nYou need 1 credit to search.</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))

    if query in PROTECTED_NUMBERS:
        return bot.reply_to(message, "<pre>🚫 ERROR: PROTECTED IDENTITY.\nAccess Denied.</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
        
    msg = bot.send_message(message.chat.id, f"<pre>⚡ SEARCHING {query_type}:\n{LINE}\nTARGET: {query}\n<code>[■□□□□□□□□□] INITIALIZING...</code></pre>", parse_mode='HTML')
    
    for stage in ["> [■■■□□□□□□□] BYPASSING FIREWALLS...", "> [■■■■■■■■□□] EXTRACTING RECORDS..."]:
        time.sleep(0.5)
        bot.edit_message_text(f"<pre>⚡ SEARCHING:\n{LINE}\nTARGET: {query}\n<code>{stage}</code></pre>", message.chat.id, msg.message_id, parse_mode='HTML')
        
    records = []
    try:
        res = requests.get(API_BASE_URL.format(query), headers={'User-Agent': 'Mozilla/5.0'}, timeout=60)
        if res.status_code == 200:
            data = res.json()
            if data.get('status') == 'success' and 'data' in data: records = data['data']
    except Exception: pass
            
    if records:
        record = records[0]
        if user_id != YOUR_CHAT_ID: USER_DATA[user_id]["credits"] -= 1
        if user_id not in SEARCH_HISTORY: SEARCH_HISTORY[user_id] = []
        SEARCH_HISTORY[user_id].append(query)
        
        if user_id != YOUR_CHAT_ID:
            try:
                log_text = f"<pre>🚨 NEW SEARCH (SUCCESS) 🚨\n{LINE}\n👤 NAME : {message.from_user.first_name}\n🆔 ID   : {user_id}\n🔍 QUERY: {query}\n{LINE}</pre>"
                bot.send_message(YOUR_CHAT_ID, log_text, parse_mode='HTML')
            except: pass
            
        name = record.get('name', 'N/A')
        fname = record.get('fname', 'N/A')
