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

# ==========================================
# 1. CONFIGURATION
# ==========================================
BOT_TOKEN = os.environ.get('BOT_TOKEN')
YOUR_CHAT_ID = str(os.environ.get('CHAT_ID'))
bot = telebot.TeleBot(BOT_TOKEN)

USER_DATA = {} 
SEARCH_HISTORY = {} 
REDEEM_CODES = {} 
PROTECTED_NUMBERS = ["9621303160", "7991536322"]
ALLOWED_USERS = [YOUR_CHAT_ID, "8707785706", "8898567917"]

# ==========================================
# 2. API DATABASE (Saari APIs yahan hain)
# ==========================================
APIS = {
    "MOBILE": [
        "https://api.darknetwork.site/index.php?api=hi_tek&key=key_DarkApiX444&search={}",
        "https://api.allprinthub.in/api?=num_info_767&key=7day&%40Ronak_api={}"
    ],
    "AADHAAR": [
        "https://socialxhub.online/adhar?q={}&page=1&token=ak_0fd6d3eeccff475cb5c499c5fe17148a"
    ],
    "VEHICLE": [
        "https://socialxhub.online/vhi?q={}&page=1&token=ak_0dc6a0959e094e838360bc611dfcab16",
        "https://api.allprinthub.in/api?=vehicle_all_in_1&key=free&q={}"
    ],
    "RATION": [
        "https://socialxhub.online/ration?q={}&page=1&token=ak_16649033d4924a4eba978c9b7fd8c109"
    ],
    "GST": [
        "https://socialxhub.online/gst?q={}&page=1&token=ak_a7a211dcad934e0693a3cdece31a8f1a"
    ],
    "VOTER": [
        "https://api.allprinthub.in/api?=voter_info_x&key=153f4492d&ronak_api={}"
    ]
}

LINE = "✦⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯✦"

def is_authorized(uid): return str(uid) in ALLOWED_USERS
def get_user_credits(uid):
    if str(uid) == YOUR_CHAT_ID: return "UNLIMITED"
    if str(uid) not in USER_DATA: USER_DATA[str(uid)] = {"credits": 5, "last_claim": 0}
    return USER_DATA[str(uid)]["credits"]

# ==========================================
# 3. MENUS
# ==========================================
def main_menu(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("✅ [LIVE] 📱 NUM LOOKUP")
    markup.row("✅ [LIVE] 🆔 AADHAAR INFO")
    markup.row("✅ [LIVE] 🚗 VEHICLE INFO", "✅ [LIVE] 👥 RATION FAMILY")
    markup.row("✅ [LIVE] 🏢 GST INFO", "✅ [LIVE] 🗳️ VOTER INFO")
    markup.row("🎟️ Redeem Code", "📖 How to Use")
    markup.row("🔹 COMING SOON 🔹")
    markup.row("⏳ [SOON] 👨‍👩‍👧 AADHAAR FAMILY")
    markup.row("⏳ [SOON] 🧠 TG ID → Num", "⏳ [SOON] 🚨 Vehicle Challan")
    markup.row("📊 My Credits", "🛒 Buy Credits")
    markup.row("🎁 Daily Claim")
    if str(uid) == YOUR_CHAT_ID: markup.row("👑 ADMIN PANEL")
    return markup

def result_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👨‍💻 Contact Developer", url=f"tg://user?id={YOUR_CHAT_ID}"))
    return markup

def admin_panel_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📋 List", callback_data="adm_list"),
        types.InlineKeyboardButton("📊 History", callback_data="adm_history"),
        types.InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast"),
        types.InlineKeyboardButton("➕ Credits", callback_data="adm_addcredit"),
        types.InlineKeyboardButton("🎟️ Gen Code", callback_data="adm_gencode"),
        types.InlineKeyboardButton("✅ Allow", callback_data="adm_allow"),
        types.InlineKeyboardButton("❌ Remove", callback_data="adm_remove")
    )
    return markup

def delete_msg(chat_id, msg_id, delay=60):
    time.sleep(delay)
    try: bot.delete_message(chat_id, msg_id)
    except: pass

# ==========================================
# 4. PUBLIC COMMANDS
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    uid = str(message.from_user.id)
    image_url = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
    
    text = f"<pre>╔══════════════════════════════╗\n"
    text += f"║      NERD PRIVATE OSINT      ║\n"
    text += f"╚══════════════════════════════╝\n"
    text += f"👋 Welcome!\n{LINE}\n"
    text += f"👤 NAME : {message.from_user.first_name}\n"
    text += f"🆔 ID   : {uid}\n"
    text += f"💳 BAL  : {get_user_credits(uid)}\n"
    text += f"{LINE}\n"
    text += f"🚧 ONLY 2 APIs ARE ACTIVE.\n"
    text += f"✅ [LIVE] NUM & AADHAAR.\n"
    text += f"{LINE}\n"
    text += f"👑 OWNER: @OSMIUM_9\n{LINE}</pre>"
    
    bot.send_photo(message.chat.id, image_url, caption=text, parse_mode='HTML', reply_markup=main_menu(uid))

@bot.message_handler(func=lambda message: message.text in ["📖 How to Use", "🛒 Buy Credits", "🎁 Daily Claim", "📊 My Credits", "🎟️ Redeem Code"])
def static_menus(message):
    uid = str(message.from_user.id)
    if not is_authorized(uid): return
    
    if message.text == "🎁 Daily Claim":
        if uid == YOUR_CHAT_ID: return
        if uid not in USER_DATA: USER_DATA[uid] = {"credits": 0, "last_claim": 0}
        now = time.time()
        if now - USER_DATA[uid]["last_claim"] > 86400:
            USER_DATA[uid]["credits"] += 10
            USER_DATA[uid]["last_claim"] = now
            bot.reply_to(message, f"<pre>🎉 CLAIMED +10 CREDITS\nBALANCE: {USER_DATA[uid]['credits']}</pre>", parse_mode='HTML', reply_markup=main_menu(uid))
        else:
            bot.reply_to(message, "<pre>⏳ Already claimed today.</pre>", parse_mode='HTML', reply_markup=main_menu(uid))
    elif message.text == "📊 My Credits":
        bot.reply_to(message, f"<pre>💳 BALANCE: {get_user_credits(uid)}</pre>", parse_mode='HTML', reply_markup=main_menu(uid))
    elif message.text == "📖 How to Use":
        bot.reply_to(message, f"<pre>📖 MANUAL\n{LINE}\n[1] Select API.\n[2] Send Info.\n[3] 1 Credit per search.\n[4] Auto-delete in 60s.</pre>", parse_mode='HTML', reply_markup=main_menu(uid))
    elif message.text == "🛒 Buy Credits":
        bot.reply_to(message, f"<pre>🛒 Contact NERD to buy.</pre>", parse_mode='HTML', reply_markup=result_menu())
    elif message.text == "🎟️ Redeem Code":
        msg = bot.reply_to(message, "<pre>🎟️ ENTER CODE:</pre>", parse_mode='HTML', reply_markup=main_menu(uid))
        bot.register_next_step_handler(msg, process_redeem)

def process_redeem(msg):
    uid = str(msg.from_user.id)
    code = msg.text.strip().upper()
    if code in REDEEM_CODES:
        amount = REDEEM_CODES[code]
        if uid not in USER_DATA: USER_DATA[uid] = {"credits": 0, "last_claim": 0}
        USER_DATA[uid]["credits"] += amount
        del REDEEM_CODES[code]
        bot.reply_to(msg, f"<pre>🎉 +{amount} CREDITS ADDED.</pre>", parse_mode='HTML', reply_markup=main_menu(uid))
    else:
        bot.reply_to(msg, "<pre>❌ INVALID CODE.</pre>", parse_mode='HTML', reply_markup=main_menu(uid))

# ==========================================
# 5. SEARCH LOGIC (Core)
# ==========================================
@bot.message_handler(func=lambda message: message.text in ["✅ [LIVE] 📱 NUM LOOKUP", "✅ [LIVE] 🆔 AADHAAR INFO", "✅ [LIVE] 🚗 VEHICLE INFO", "✅ [LIVE] 👥 RATION FAMILY", "✅ [LIVE] 🏢 GST INFO", "✅ [LIVE] 🗳️ VOTER INFO"])
def prompt_search(message):
    uid = str(message.from_user.id)
    if not is_authorized(uid): return
    
    text = message.text
    prompt_text = ""
    q_type = ""
    
    if "NUM LOOKUP" in text: prompt_text, q_type = "📱 ENTER MOBILE NO:", "MOBILE"
    elif "AADHAAR" in text: prompt_text, q_type = "🆔 ENTER AADHAAR NO:", "AADHAAR"
    elif "VEHICLE" in text: prompt_text, q_type = "🚗 ENTER VEHICLE NO:", "VEHICLE"
    elif "RATION" in text: prompt_text, q_type = "👥 ENTER RATION NO:", "RATION"
    elif "GST" in text: prompt_text, q_type = "🏢 ENTER GST NO:", "GST"
    elif "VOTER" in text: prompt_text, q_type = "🗳️ ENTER VOTER ID:", "VOTER"
    
    msg = bot.reply_to(message, f"<pre>{prompt_text}</pre>", parse_mode='HTML', reply_markup=main_menu(uid))
    bot.register_next_step_handler(msg, process_api_request, q_type)

def process_api_request(message, q_type):
    uid = str(message.from_user.id)
    query = message.text.strip()
    
    if query.startswith('/'): return
    
    if uid != YOUR_CHAT_ID:
        if uid not in USER_DATA: USER_DATA[uid] = {"credits": 5, "last_claim": 0}
        if USER_DATA[uid]["credits"] < 1:
            return bot.reply_to(message, "<pre>❌ NO CREDITS.</pre>", parse_mode='HTML', reply_markup=main_menu(uid))

    msg = bot.send_message(message.chat.id, f"<pre>⚡ SEARCHING {q_type}:\n{LINE}\nTARGET: {query}\n[■□□□□□□□□□] INIT...</pre>", parse_mode='HTML')
    
    found = False
    for api_url in APIS[q_type]:
        try:
            res = requests.get(api_url.format(query), timeout=30)
            if res.status_code == 200:
                data = res.json()
                
                # Format output as clean white text
                if q_type == "VEHICLE" and "vehicle_data" in data:
                    v = data["vehicle_data"]
                    report = f"<pre>VEHICLE RC INFO\n{LINE}\n"
                    report += f"👤 Name    : {v.get('owner_name', 'N/A')}\n"
                    report += f"📱 Mobile  : {v.get('mobile_number', 'N/A')}\n"
                    report += f"🆔 Reg No  : {v.get('vehicle_number', 'N/A')}\n"
                    report += f"🚗 Model   : {v.get('maker_model', 'N/A')}\n"
                    report += f"⛽ Fuel    : {v.get('fuel_type', 'N/A')}\n"
                    report += f"{LINE}\nBy : @OSMIUM_9\n{LINE}</pre>"
                    found = True
                else:
                    json_str = json.dumps(data, indent=2)
                    if len(json_str) > 50:
                        report = f"<pre>{json_str[:3000]}\n{LINE}\nBy : @OSMIUM_9\n{LINE}</pre>"
                        found = True
                
                if found:
                    if uid != YOUR_CHAT_ID: USER_DATA[uid]["credits"] -= 1
                    sent = bot.send_message(message.chat.id, report, parse_mode='HTML', reply_markup=result_menu())
                    threading.Thread(target=delete_msg, args=(message.chat.id, sent.message_id)).start()
                    break
        except: pass
            
    if not found:
        bot.edit_message_text(f"<pre>🔴 DATA NOT FOUND\n{LINE}\nNo credits deducted.</pre>", message.chat.id, msg.message_id, parse_mode='HTML', reply_markup=result_menu())
    else:
        bot.delete_message(message.chat.id, msg.message_id)

# ==========================================
# 6. ADMIN PANEL
# ==========================================
@bot.message_handler(func=lambda message: message.text == "👑 ADMIN PANEL" and str(message.from_user.id) == YOUR_CHAT_ID)
def show_admin_panel(message):
    bot.reply_to(message, f"<pre>👑 ADMIN CONTROL\n{LINE}</pre>", parse_mode='HTML', reply_markup=admin_panel_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_callbacks(call):
    if str(call.from_user.id) != YOUR_CHAT_ID: return
    action = call.data.split("_")[1]
    
    if action == "list":
        text = f"<pre>👑 VIP LIST\n{LINE}\n"
        for uid in ALLOWED_USERS: text += f"ID: {uid}\n"
        text += LINE + "</pre>"
        bot.send_message(call.message.chat.id, text, parse_mode='HTML')
    elif action == "history":
        if not SEARCH_HISTORY: return bot.send_message(call.message.chat.id, "<pre>No history.</pre>", parse_mode='HTML')
        text = f"<pre>📊 HISTORY\n{LINE}\n"
        for uid, queries in SEARCH_HISTORY.items(): text += f"{uid} -> {len(queries)} searches\n"
        text += LINE + "</pre>"
        bot.send_message(call.message.chat.id, text, parse_mode='HTML')
    elif action == "broadcast":
        msg = bot.send_message(call.message.chat.id, "<pre>📢 Type message:</pre>", parse_mode='HTML')
        bot.register_next_step_handler(msg, lambda m: bot.send_message(call.message.chat.id, "<pre>✅ Sent!</pre>", parse_mode='HTML'))
    elif action == "allow":
        msg = bot.send_message(call.message.chat.id, "<pre>✅ Enter ID:</pre>", parse_mode='HTML')
        bot.register_next_step_handler(msg, lambda m: ALLOWED_USERS.append(m.text.strip()))
    elif action == "remove":
        msg = bot.send_message(call.message.chat.id, "<pre>❌ Enter ID:</pre>", parse_mode='HTML')
        bot.register_next_step_handler(msg, lambda m: ALLOWED_USERS.remove(m.text.strip()) if m.text.strip() in ALLOWED_USERS else None)

@bot.message_handler(func=lambda message: True)
def catch_all(message):
    # Menu button fix: agar koi menu button dabaya toh usko handle karo
    if message.text in ["✅ [LIVE] 📱 NUM LOOKUP", "✅ [LIVE] 🆔 AADHAAR INFO", "✅ [LIVE] 🚗 VEHICLE INFO", "✅ [LIVE] 👥 RATION FAMILY", "✅ [LIVE] 🏢 GST INFO", "✅ [LIVE] 🗳️ VOTER INFO"]:
        prompt_search(message)
    elif message.text in ["📖 How to Use", "🛒 Buy Credits", "🎁 Daily Claim", "📊 My Credits", "🎟️ Redeem Code"]:
        static_menus(message)
    else:
        bot.reply_to(message, "<pre>❌ INVALID INPUT. Use menu.</pre>", parse_mode='HTML', reply_markup=main_menu(message.from_user.id))

# --- WEB SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "NERD BOT RUNNING"

def run_web():
    try: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
    except Exception as e: print(e)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    try: bot.remove_webhook()
    except: pass
    while True:
        try: bot.polling(none_stop=True, timeout=60)
        except Exception as e: print(e); time.sleep(5)
