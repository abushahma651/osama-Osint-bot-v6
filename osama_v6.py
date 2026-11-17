from flask import Flask
import threading
import os
import telebot
import requests
import time
import random
import string
import json
from telebot import types

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
YOUR_CHAT_ID = str(os.environ.get('CHAT_ID'))
bot = telebot.TeleBot(BOT_TOKEN)

# --- DATABASE ---
USER_DATA = {} 
SEARCH_HISTORY = {} 
REDEEM_CODES = {} 
PROTECTED_NUMBERS = ["9621303160", "7991536322", "8604302624", "6204473620"]
ALLOWED_USERS = [YOUR_CHAT_ID, "8707785706", "8898567917", "6700078527", "5704555109", "901112667", "8659201578"]

# --- APIs ---
MOBILE_APIS = [
    "https://api.darknetwork.site/index.php?api=hi_tek&key=key_DarkApiX444&search={}",
    "https://api.allprinthub.in/api?=num_info_767&key=7day&%40Ronak_api={}"
]
AADHAAR_APIS = ["https://socialxhub.online/adhar?q={}&page=1&token=ak_0fd6d3eeccff475cb5c499c5fe17148a"]
VEHICLE_APIS = [
    "https://socialxhub.online/vhi?q={}&page=1&token=ak_0dc6a0959e094e838360bc611dfcab16",
    "https://api.allprinthub.in/api?=vehicle_all_in_1&key=free&q={}"
]
RATION_APIS = ["https://socialxhub.online/ration?q={}&page=1&token=ak_16649033d4924a4eba978c9b7fd8c109"]
GST_APIS = ["https://socialxhub.online/gst?q={}&page=1&token=ak_a7a211dcad934e0693a3cdece31a8f1a"]
FAMILY_APIS = ["https://api.allprinthub.in/api?=adhaar_to_family_680&key=f4328e3c255b18&q={}"]
VOTER_APIS = ["https://api.allprinthub.in/api?=voter_info_x&key=153f4492d&ronak_api={}"]

BTN_NUM = "✅ [LIVE] 📱 NUM LOOKUP"
BTN_AADHAAR = "✅ [LIVE] 🆔 AADHAAR INFO"
BTN_VEHICLE = "✅ [LIVE] 🚗 VEHICLE INFO"
BTN_RATION = "✅ [LIVE] 👥 RATION FAMILY"
BTN_GST = "✅ [LIVE] 🏢 GST INFO"
BTN_FAMILY = "✅ [LIVE] 👨‍👩‍👧 AADHAAR FAMILY"
BTN_VOTER = "✅ [LIVE] 🗳️ VOTER INFO"
LINE = "✦⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯✦"

def is_authorized(user_id):
    return str(user_id) in ALLOWED_USERS

def get_user_credits(user_id):
    user_id = str(user_id)
    if user_id == YOUR_CHAT_ID: return "UNLIMITED"
    if user_id not in USER_DATA: USER_DATA[user_id] = {"credits": 5, "last_claim": 0}
    return USER_DATA[user_id]["credits"]

def generate_code(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for i in range(length))

# --- KEYBOARDS ---
def main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(BTN_NUM)
    markup.row(BTN_AADHAAR)
    markup.row(BTN_VEHICLE, BTN_RATION)
    markup.row(BTN_GST, BTN_FAMILY)
    markup.row(BTN_VOTER, "🎟️ Redeem Code")
    markup.row("🔹 COMING SOON FEATURES 🔹")
    markup.row("⏳ [SOON] 🧠 TG ID → Num", "⏳ [SOON] 📧 Email → Num")
    markup.row("⏳ [SOON] 🚨 Vehicle Challan", "⏳ [SOON] 📸 Instagram Info")
    markup.row("⏳ [SOON] 💳 PAN Info", "⏳ [SOON] 🎮 BGMI Info")
    markup.row("📊 My Credits", "🛒 Buy Credits")
    markup.row("🎁 Daily Claim", "📖 How to Use")
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
    try: bot.delete_message(chat_id, message_id)
    except: pass

# =====================================================================
# 👑 ADMIN PANEL
# =====================================================================

@bot.message_handler(func=lambda message: message.text == "👑 ADMIN PANEL" and str(message.from_user.id) == YOUR_CHAT_ID)
def show_admin_panel(message):
    bot.reply_to(message, f"<pre>👑 OWNER CONTROL PANEL\n{LINE}\nSelect an action:</pre>", parse_mode='HTML', reply_markup=admin_panel_menu())

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
            try: name = bot.get_chat(uid).first_name
            except: name = "Unknown"
            text += f"{i}. {name} | {uid}\n"
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
        msg = bot.send_message(call.message.chat.id, "<pre>📢 Enter message:</pre>", parse_mode='HTML')
        bot.register_next_step_handler(msg, lambda m: process_broadcast(m))
    elif action == "addcredit":
        msg = bot.send_message(call.message.chat.id, "<pre>➕ Format: 123456789 50</pre>", parse_mode='HTML')
        bot.register_next_step_handler(msg, lambda m: process_addcredit(m))
    elif action == "gencode":
        msg = bot.send_message(call.message.chat.id, "<pre>🎟️ Enter amount:</pre>", parse_mode='HTML')
        bot.register_next_step_handler(msg, lambda m: process_gencode(m))
    elif action == "allow":
        msg = bot.send_message(call.message.chat.id, "<pre>✅ Enter User ID:</pre>", parse_mode='HTML')
        bot.register_next_step_handler(msg, lambda m: process_allow(m))
    elif action == "remove":
        msg = bot.send_message(call.message.chat.id, "<pre>❌ Enter User ID:</pre>", parse_mode='HTML')
        bot.register_next_step_handler(msg, lambda m: process_remove(m))

def process_broadcast(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    success = 0
    for uid in ALLOWED_USERS:
        try:
            bot.send_message(uid, f"<pre>📢 BROADCAST\n{LINE}\n{message.text}\n{LINE}</pre>", parse_mode='HTML')
            success += 1
        except: pass
    bot.reply_to(message, f"<pre>✅ Sent to {success} users.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

def process_addcredit(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    try:
        args = message.text.split()
        target_id, amount = args[0], int(args[1])
        if target_id not in USER_DATA: USER_DATA[target_id] = {"credits": 0, "last_claim": 0}
        USER_DATA[target_id]["credits"] += amount
        bot.reply_to(message, f"<pre>✅ Added {amount} credits to {target_id}.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))
    except: bot.reply_to(message, "<pre>❌ Invalid format.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

def process_gencode(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    try:
        amount = int(message.text)
        code = generate_code()
        REDEEM_CODES[code] = amount
        bot.reply_to(message, f"<pre>🎟️ CODE: {code}\nVALUE: {amount} Credits</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))
    except: bot.reply_to(message, "<pre>❌ Invalid amount.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

def process_allow(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    new_id = message.text.strip()
    if new_id not in ALLOWED_USERS:
        ALLOWED_USERS.append(new_id)
        bot.reply_to(message, f"<pre>✅ User {new_id} allowed.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))
    else: bot.reply_to(message, "<pre>⚠️ Already allowed.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

def process_remove(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    rem_id = message.text.strip()
    if rem_id in ALLOWED_USERS and rem_id != YOUR_CHAT_ID:
        ALLOWED_USERS.remove(rem_id)
        bot.reply_to(message, f"<pre>✅ User {rem_id} removed.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))
    else: bot.reply_to(message, "<pre>⚠️ User not found.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

# =====================================================================
# 🤖 PUBLIC COMMANDS
# =====================================================================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    image_url = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
    text = f"<pre>╔══════════════════════════════╗\n║      NERD PRIVATE OSINT      ║\n╚══════════════════════════════╝\n👋 Welcome!\n{LINE}\n👤 NAME    : {message.from_user.first_name}\n🆔 USER ID : {user_id}\n💳 CREDITS : {get_user_credits(user_id)}\n{LINE}\n✨ SERVICES: ALL LIVE\n{LINE}\n👑 OWNER — @OSMIUM_9\n{LINE}</pre>"
    bot.send_photo(message.chat.id, image_url, caption=text, parse_mode='HTML', reply_markup=main_menu(user_id))

@bot.message_handler(func=lambda message: message.text in ["📖 How to Use", "🛒 Buy Credits", "🎁 Daily Claim", "📊 My Credits", "🎟️ Redeem Code"])
def static_menus(message):
    if not is_authorized(message.from_user.id): return send_access_denied(message)
    user_id = str(message.from_user.id)
    
    if message.text == "📖 How to Use":
        bot.reply_to(message, f"<pre>📖 MANUAL\n{LINE}\n[1] Select feature.\n[2] Send info.\n[3] Cost: 1 credit.\n[4] Reports delete in 60s.\n{LINE}\nSUPPORT: @OSMIUM_9</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
    elif message.text == "🛒 Buy Credits":
        bot.reply_to(message, f"<pre>🛒 BUY CREDITS\n{LINE}\nContact NERD below.</pre>", parse_mode='HTML', reply_markup=result_menu())
    elif message.text == "🎁 Daily Claim":
        if user_id == YOUR_CHAT_ID:
            bot.reply_to(message, "<pre>👑 OWNER: UNLIMITED</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
            return
        if user_id not in USER_DATA: USER_DATA[user_id] = {"credits": 0, "last_claim": 0}
        now = time.time()
        if now - USER_DATA[user_id]["last_claim"] < 86400:
            rem = 86400 - (now - USER_DATA[user_id]["last_claim"])
            bot.reply_to(message, f"<pre>⏳ CLAIM BLOCKED\n{LINE}\nTIME: {int(rem//3600)}h {int((rem%3600)//60)}m</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
            return
        USER_DATA[user_id]["credits"] += 10
        USER_DATA[user_id]["last_claim"] = now
        bot.reply_to(message, f"<pre>🎉 CLAIMED\n{LINE}\n+10 CREDITS\nBAL: {USER_DATA[user_id]['credits']}</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
    elif message.text == "📊 My Credits":
        bot.reply_to(message, f"<pre>💳 BALANCE\n{LINE}\nID : {user_id}\nBAL: {get_user_credits(user_id)}</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
    elif message.text == "🎟️ Redeem Code":
        msg = bot.reply_to(message, "<pre>🎟️ ENTER CODE:</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
        bot.register_next_step_handler(msg, process_redeem)

def process_redeem(msg):
    if msg.text.startswith('/') or msg.text in [BTN_NUM, BTN_AADHAAR]: bot.clear_step_handler(msg); return
    user_id = str(msg.from_user.id)
    code = msg.text.strip().upper()
    if code in REDEEM_CODES:
        amount = REDEEM_CODES[code]
        if user_id not in USER_DATA: USER_DATA[user_id] = {"credits": 0, "last_claim": 0}
        USER_DATA[user_id]["credits"] += amount
        del REDEEM_CODES[code]
        bot.reply_to(msg, f"<pre>🎉 REDEEMED\n{LINE}\n+{amount} CREDITS\nBAL: {USER_DATA[user_id]['credits']}</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
    else: bot.reply_to(msg, "<pre>❌ INVALID CODE.</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))

# =====================================================================
# 🔍 SEARCH LOGIC
# =====================================================================

def process_api_request(message, query_type, apis):
    user_id = str(message.from_user.id)
    if not is_authorized(user_id): return send_access_denied(message)
    query = message.text.strip()
    
    if query.startswith('/'): return
        
    if user_id != YOUR_CHAT_ID:
        if user_id not in USER_DATA: USER_DATA[user_id] = {"credits": 5, "last_claim": 0}
        if USER_DATA[user_id]["credits"] < 1:
            return bot.reply_to(message, "<pre>❌ NO CREDITS.</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))

    if query in PROTECTED_NUMBERS:
        return bot.reply_to(message, "<pre>🚫 PROTECTED.</pre>", parse_mode='HTML', reply_markup=main_menu(user_id))
        
    msg = bot.send_message(message.chat.id, f"<pre>⚡ SEARCHING {query_type}:\n{LINE}\nTARGET: {query}\n<code>[■□□□□□□□□□] INIT...</code></pre>", parse_mode='HTML')
    
    found_any = False
    for api_url in apis:
        try:
            res = requests.get(api_url.format(query), headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
            if res.status_code == 200:
                data = res.json()
                json_str = json.dumps(data, indent=2)
                if len(json_str) > 50 and "error" not in json_str.lower():
                    found_any = True
                    if user_id != YOUR_CHAT_ID: USER_DATA[user_id]["credits"] -= 1
                    
                    report = f"<pre>NERD OSINT REPORT\n{LINE}\nQUERY: {query}\nTYPE : {query_type}\n{LINE}\n{json_str[:3000]}\n{LINE}\nBy : @OSMIUM_9\n{LINE}\n⚠️ DELETE IN 60s.\n</pre>"
                    sent = bot.send_message(message.chat.id, report, parse_mode='HTML', reply_markup=result_menu())
                    threading.Thread(target=delete_message_later, args=(message.chat.id, sent.message_id, 60)).start()
        except: pass
            
    if found_any:
        bot.delete_message(message.chat.id, msg.message_id)
    else:
        bot.edit_message_text(text=f"<pre>🔴 NOT FOUND\n{LINE}\nTARGET: {query}\nNo credits deducted.</pre>", chat_id=message.chat.id, message_id=msg.message_id, parse_mode='HTML', reply_markup=result_menu())

# =====================================================================
# 🔍 MENU HANDLERS
# =====================================================================

@bot.message_handler(func=lambda message: message.text in [BTN_NUM, BTN_AADHAAR, BTN_VEHICLE, BTN_RATION, BTN_GST, BTN_FAMILY, BTN_VOTER])
def prompt_search(message):
    if not is_authorized(message.from_user.id): return send_access_denied(message)
    uid = str(message.from_user.id)
    
    if message.text == BTN_NUM:
        bot.register_next_step_handler(bot.reply_to(message, "<pre>📱 ENTER MOBILE:</pre>", parse_mode='HTML', reply_markup=main_menu(uid)), process_api_request, "MOBILE", MOBILE_APIS)
    elif message.text == BTN_AADHAAR:
        bot.register_next_step_handler(bot.reply_to(message, "<pre>🆔 ENTER AADHAAR:</pre>", parse_mode='HTML', reply_markup=main_menu(uid)), process_api_request, "AADHAAR", AADHAAR_APIS)
    elif message.text == BTN_VEHICLE:
        bot.register_next_step_handler(bot.reply_to(message, "<pre>🚗 ENTER VEHICLE NO:</pre>", parse_mode='HTML', reply_markup=main_menu(uid)), process_api_request, "VEHICLE", VEHICLE_APIS)
    elif message.text == BTN_RATION:
        bot.register_next_step_handler(bot.reply_to(message, "<pre>👥 ENTER RATION NO:</pre>", parse_mode='HTML', reply_markup=main_menu(uid)), process_api_request, "RATION", RATION_APIS)
    elif message.text == BTN_GST:
        bot.register_next_step_handler(bot.reply_to(message, "<pre>🏢 ENTER GST NO:</pre>", parse_mode='HTML', reply_markup=main_menu(uid)), process_api_request, "GST", GST_APIS)
    elif message.text == BTN_FAMILY:
        bot.register_next_step_handler(bot.reply_to(message, "<pre>👨‍👩‍👧 ENTER AADHAAR:</pre>", parse_mode='HTML', reply_markup=main_menu(uid)), process_api_request, "FAMILY", FAMILY_APIS)
    elif message.text == BTN_VOTER:
        bot.register_next_step_handler(bot.reply_to(message, "<pre>🗳️ ENTER VOTER ID:</pre>", parse_mode='HTML', reply_markup=main_menu(uid)), process_api_request, "VOTER", VOTER_APIS)

@bot.message_handler(func=lambda message: True)
def invalid_input(message):
    if not is_authorized(message.from_user.id): return send_access_denied(message)
    bot.reply_to(message, "<pre>❌ INVALID.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

# --- WEB SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "NERD OSINT BOT IS RUNNING!"

def run_web():
    try:
        app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
    except Exception as e:
        print(f"Web error: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    try: bot.remove_webhook()
    except: pass
    
    while True:
        try: bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"Poll error: {e}")
            time.sleep(5)
