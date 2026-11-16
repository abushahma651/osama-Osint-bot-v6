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
    "8707785706",       # VIP 1
    "8898567917",       # VIP 2
    "6700078527",       # VIP 3
    "5704555109",       # VIP 4
    "901112667",        # VIP 5 
    "8659201578"        # VIP 6
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

# --- KEYBOARDS ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📱 Indian Number", "🆔 Aadhaar Info")
    markup.row("☎️ Truecaller", "📍 Tracker")
    markup.row("🚗 Vehicle", "🏦 IFSC", "📲 IMEI")
    markup.row("🌐 IP", "📍 Pincode", "🏢 GST")
    markup.row("📸 Instagram", "✈️ TG to Number")
    markup.row("💳 PAN Lookup", "🔗 PAN GST", "🎮 Free Fire ID")
    markup.row("🇵🇰 CNIC Lookup", "✉️ SMS", "🚨 Chalan")
    markup.row("💳 UPI", "👨‍👩‍👧 Family", "🔍 Name Search")
    markup.row("🚗➡️📱 Vehicle to Num", "💰 Fampay")
    markup.row("🎁 Refer & Earn", "🪙 Check Credits")
    markup.row("🎁 Daily Claim", "🛒 Buy Credits")
    return markup

def result_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_dev = types.InlineKeyboardButton("👨‍💻 Contact Developer (NERD)", url=f"tg://user?id={YOUR_CHAT_ID}")
    markup.add(btn_dev)
    return markup

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
    
    # 🚫 NEW USERS BLOCKED
    if not is_authorized(user_id):
        bot.reply_to(
            message, 
            "🚫 <b>ACCESS DENIED</b>\n\n"
            "This is a private OSINT tool. You do not have permission to use it.\n\n"
            "👉 <b>To get VIP access and credits, please contact NERD via the button below.</b>", 
            parse_mode='HTML',
            reply_markup=result_menu()
        )
        return

    # Authorized User Check
    credits = get_user_credits(user_id)
    
    # 👇 YAHAN NAAM CHANGE HUA HAI 👇
    text = (
        "🟢 <b>NERD PRIVATE OSINT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Welcome back to NERD PRIVATE OSINT.\n"
        f"💳 <b>Your Credits:</b> {credits}\n\n"
        "Select an option from the menu below.\n"
        "⚠️ <i>Reports will auto-delete in 60 seconds.</i>"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=main_menu())

# --- DAILY CLAIM ---
@bot.message_handler(func=lambda message: message.text == "🎁 Daily Claim")
def daily_claim(message):
    user_id = str(message.from_user.id)
    if not is_authorized(user_id): return
    
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
@bot.message_handler(func=lambda message: message.text == "🪙 Check Credits")
def check_credits(message):
    user_id = str(message.from_user.id)
    if not is_authorized(user_id): return
    credits = get_user_credits(user_id)
    bot.reply_to(message, f"💳 <b>Your Balance:</b> {credits}\n\nContact NERD to buy more credits.", parse_mode='HTML', reply_markup=main_menu())

# --- WORKING API PROMPTS ---
@bot.message_handler(func=lambda message: message.text == "📱 Indian Number")
def prompt_mobile(message):
    if not is_authorized(message.from_user.id): return
    msg = bot.reply_to(message, "📱 <b>Enter a 10-digit Mobile Number to search:</b>", parse_mode='HTML', reply_markup=main_menu())
    bot.register_next_step_handler(msg, process_search, "MOBILE")

@bot.message_handler(func=lambda message: message.text == "🆔 Aadhaar Info")
def prompt_aadhaar(message):
    if not is_authorized(message.from_user.id): return
    msg = bot.reply_to(message, "🆔 <b>Enter a 12-digit Aadhaar Number to search:</b>", parse_mode='HTML', reply_markup=main_menu())
    bot.register_next_step_handler(msg, process_search, "AADHAAR")

# --- "COMING SOON" ---
@bot.message_handler(func=lambda message: message.text in ["☎️ Truecaller", "📍 Tracker", "🚗 Vehicle", "🏦 IFSC", "📲 IMEI", "🌐 IP", "📍 Pincode", "🏢 GST", "📸 Instagram", "✈️ TG to Number", "💳 PAN Lookup", "🔗 PAN GST", "🎮 Free Fire ID", "🇵🇰 CNIC Lookup", "✉️ SMS", "🚨 Chalan", "💳 UPI", "👨‍👩‍👧 Family", "🔍 Name Search", "🚗➡️📱 Vehicle to Num", "💰 Fampay", "🎁 Refer & Earn", "🛒 Buy Credits"])
def coming_soon(message):
    if not is_authorized(message.from_user.id): return
    bot.reply_to(message, "⚠️ <b>Soon this service will start.</b>\nStay tuned for the next update by NERD.", parse_mode='HTML', reply_markup=main_menu())

# --- HISTORY COMMAND (OWNER ONLY) ---
@bot.message_handler(commands=['history'])
def owner_history(message):
    if str(message.from_user.id) != YOUR_CHAT_ID: return
    
    if not SEARCH_HISTORY:
        bot.reply_to(message, "No searches yet.")
        return
        
    text = "📊 <b>USER SEARCH HISTORY</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
    for uid, queries in SEARCH_HISTORY.items():
        text += f"👤 <b>User:</b> <code>{uid}</code>\n"
        text += f"🔍 <b>Queries:</b> {', '.join(queries[-5:])} (Last 5)\n"
        text += f"📈 <b>Total:</b> {len(queries)}\n\n"
    bot.reply_to(message, text, parse_mode='HTML')

# --- MAIN SEARCH FUNCTION ---
def process_search(message, query_type, direct_query=None):
    user_id = str(message.from_user.id)
    if not is_authorized(user_id): return

    query = direct_query if direct_query else message.text.strip()
    
    if query in ["📱 Indian Number", "🆔 Aadhaar Info"]:
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

        # 👇 YAHAN BHI REPORT KA NAAM CHANGE HUA HAI 👇
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
            "</pre>"
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
        bot.reply_to(message, "🚫 ACCESS DENIED.", reply_markup=result_menu())
        return
    bot.reply_to(message, "❌ Please use the menu below.", reply_markup=main_menu())

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
