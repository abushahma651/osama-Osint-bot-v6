from flask import Flask
import threading
import os
import telebot
import requests
import time
import json
from telebot import types

# --- CONFIGURATION (Render Environment Variables) ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
YOUR_CHAT_ID = os.environ.get('CHAT_ID')

# =====================================================================
# 👇 DONO APIs KE LINKS (Base URL same hai) 👇
# =====================================================================
API_BASE_URL = "https://api.darknetwork.site/index.php?api=hi_tek&key=key_DarkApiX444&search={}"
# =====================================================================

bot = telebot.TeleBot(BOT_TOKEN)

# --- SECURITY BLACKLIST (Mobile & Aadhaar dono daal sakte hain) ---
PROTECTED_NUMBERS = ["9876543210", "123456789012"] 

# --- MENU (CONTACT DEVELOPER BUTTON) ---
def get_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_dev = types.InlineKeyboardButton("👨‍💻 Contact Developer (Osama)", url=f"tg://user?id={YOUR_CHAT_ID}")
    markup.add(btn_dev)
    return markup

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (
        "🟢 <b>OSAMA OSINT ENGINE v8.0</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Send me any <b>10-digit Mobile Number</b> or <b>12-digit Aadhaar Number</b>, and I will provide you with all the details related to it.\n\n"
        "⚠️ <i>All queries are logged. Use strictly for educational purposes.</i>"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=get_menu())

# --- SCANNER HANDLER (Mobile + Aadhaar) ---
@bot.message_handler(func=lambda message: message.text.isdigit() and len(message.text) in [10, 12])
def handle_scan(message):
    query = message.text
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Check Type
    if len(query) == 10:
        query_type = "MOBILE"
    else:
        query_type = "AADHAAR"

    # 🔥 ADMIN LOGGING SYSTEM
    if str(user_id) != str(YOUR_CHAT_ID):
        log_message = (
            f"🚨 <b>NEW SEARCH DETECTED</b> 🚨\n\n"
            f"👤 <b>Name:</b> {first_name}\n"
            f"🔗 <b>Username:</b> @{username if username else 'No Username'}\n"
            f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
            f"🕵️ <b>Type:</b> {query_type}\n"
            f"🔍 <b>Searched Query:</b> <code>{query}</code>"
        )
        try:
            bot.send_message(YOUR_CHAT_ID, log_message, parse_mode='HTML')
        except Exception:
            pass

    # 🚫 BLACKLIST CHECK
    if query in PROTECTED_NUMBERS:
        bot.reply_to(
            message, 
            "🚫 <b>ACCESS DENIED</b>\n\n"
            "This identity is protected under the <b>OSAMA OSINT SECURITY PROTOCOL</b>. Unauthorized tracing is strictly prohibited.", 
            parse_mode='HTML'
        )
        return
        
    msg = bot.send_message(message.chat.id, f"⚡ <b>Searching {query_type} Database for:</b> <code>{query}</code>\n\n<code>[■□□□□□□□□□] INITIALIZING...</code>", parse_mode='HTML')
    
    # Premium Loading Animation
    stages = [
        f"> [■■■□□□□□□□] BYPASSING {query_type} FIREWALLS...",
        "> [■■■■■□□□□□] QUERYING NODES...",
        "> [■■■■■■■■□□] EXTRACTING RECORDS...",
        "> [■■■■■■■■■■] FORMATTING DATA..."
    ]
    
    for stage in stages:
        time.sleep(0.5)
        bot.edit_message_text(f"⚡ <b>Searching {query_type} Database for:</b> <code>{query}</code>\n\n<code>{stage}</code>", message.chat.id, msg.message_id, parse_mode='HTML')
        
    records = []
    
    # 🔍 API SE DATA FETCH KARNA
    try:
        res = requests.get(API_BASE_URL.format(query), timeout=20)
        if res.status_code == 200:
            data = res.json()
            if data.get('status') == 'success' and 'data' in data:
                records = data['data']
    except Exception as e:
        print(f"API Error: {e}")
            
    if records:
        # Agar multiple records hain, toh sab dikhayenge
        for idx, record in enumerate(records, 1):
            # 🛠️ Data Extraction & Cleaning
            name = record.get('name', 'N/A')
            fname = record.get('fname', 'N/A')
            
            mobile = record.get('mobile', query if query_type == "MOBILE" else 'N/A')
            alt = record.get('alt', 'None')
            if alt == 'None' or not alt: alt = 'N/A'
            
            aadhaar = record.get('id', query if query_type == "AADHAAR" else 'N/A')
            
            circle = record.get('circle', 'None')
            if circle == 'None' or not circle: circle = 'N/A'
            
            email = record.get('email', 'None')
            if email == 'None' or not email: email = 'N/A'
            
            address = record.get('address', 'N/A')
            clean_address = address.replace('!', ', ').strip(', ') if address != 'N/A' else 'N/A'

            # 📄 ELITE REPORT FORMAT
            report = (
                "<pre>"
                "OSINT LOOKUP REPORT\n\n"
                "✦⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯✦\n"
                f"👤 Query        : {query}\n"
                f"📊 Type         : {query_type}\n"
                f"📁 Record       : {idx} of {len(records)}\n"
                "✦⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯✦\n\n"
                "Record Details\n"
                "✦⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯✦\n"
                f"Name           : {name}\n"
                f"Father Name    : {fname}\n"
                f"Mobile         : {mobile}\n"
                f"Alt Number     : {alt}\n"
                f"Aadhaar No     : {aadhaar}\n"
                f"Circle         : {circle}\n"
                f"Email          : {email}\n"
                f"Address        : {clean_address}\n"
                "✦⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯✦\n\n"
                "By : @OSMIUM_9\n"
                "✦⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯✦"
                "</pre>"
            )
            
            # Har record ke liye alag message bhejenge (taaki lambe messages truncate na ho)
            if idx == 1:
                bot.edit_message_text(report, message.chat.id, msg.message_id, parse_mode='HTML', reply_markup=get_menu())
            else:
                bot.send_message(message.chat.id, report, parse_mode='HTML', reply_markup=get_menu())
                time.sleep(0.5) # Thoda gap taaki Telegram block na kare
        
    else:
        bot.edit_message_text(
            text=f"🔴 <b>DATA NOT FOUND:</b> <code>{query}</code>\n\n<i>No records found for this {query_type}.</i>",
            chat_id=message.chat.id,
            message_id=msg.message_id,
            parse_mode='HTML',
            reply_markup=get_menu()
        )

# --- INVALID INPUT HANDLER ---
@bot.message_handler(func=lambda message: True)
def invalid_input(message):
    bot.reply_to(message, "❌ <b>ERROR:</b> Invalid format. Please send a valid 10-digit Mobile Number or 12-digit Aadhaar Number.", parse_mode='HTML')

# --- DUMMY WEB SERVER (Render ke liye) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Osama OSINT Bot (Dual API) is running successfully!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    print("🤖 Osama Elite Bot v8.0 (Dual API) is running...")
    bot.polling(none_stop=True)
