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

bot = telebot.TeleBot(BOT_TOKEN)

# API NODES
APIS = [
    "https://tfqdeadlo-1-78bapi.hf.space/search?mobile={}",
    "https://tfqdeadlo-850crfastsearch.hf.space/search/{}",
    "https://tfqdeadlo-inddataapi.hf.space/search?mobile={}"
]

# --- MENU (CONTACT DEVELOPER BUTTON) ---
def get_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    # Chat ID ke through direct chat open karne ka link
    btn_dev = types.InlineKeyboardButton("👨‍💻 Contact Developer (Osama)", url=f"tg://user?id={YOUR_CHAT_ID}")
    markup.add(btn_dev)
    return markup

# --- START COMMAND (Simple & Clean) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (
        "🟢 <b>OSAMA OSINT ENGINE</b>\n\n"
        "Send me any 10-digit mobile number, and I will provide you with all the details related to it.\n\n"
        "⚠️ <i>All queries are logged. Use strictly for educational purposes.</i>"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=get_menu())

# --- SCANNER HANDLER ---
@bot.message_handler(func=lambda message: message.text.isdigit() and len(message.text) == 10)
def handle_scan(message):
    mobile = message.text
    msg = bot.send_message(message.chat.id, f"⚡ <b>Searching Database for:</b> <code>{mobile}</code>\n\n<code>[■□□□□□□□□□] INITIALIZING...</code>", parse_mode='HTML')
    
    # Premium Loading Animation
    stages = [
        "> [■■■□□□□□□□] BYPASSING FIREWALLS...",
        "> [■■■■■□□□□□] QUERYING 3 NODES...",
        "> [■■■■■■■■□□] EXTRACTING RECORDS...",
        "> [■■■■■■■■■■] FORMATTING DATA..."
    ]
    
    for stage in stages:
        time.sleep(0.6)
        bot.edit_message_text(f"⚡ <b>Searching Database for:</b> <code>{mobile}</code>\n\n<code>{stage}</code>", message.chat.id, msg.message_id, parse_mode='HTML')
        
    record = None
    
    # Try all APIs until we find a record
    for url in APIS:
        try:
            res = requests.get(url.format(mobile), timeout=10)
            data = res.json()
            
            if data and 'data' in data and data['data']:
                record = data['data']
                if isinstance(record, list): record = record[0]
                break
            elif data and data.get('mobile'):
                record = data
                break
        except Exception:
            pass
            
    if record:
        # Data Cleaning & Formatting
        name = record.get('name', 'N/A')
        fname = record.get('fname', 'N/A')
        alt = record.get('alt', 'None')
        if alt == 'None' or not alt: alt = 'N/A'
        
        circle = record.get('circle', 'None')
        if circle == 'None' or not circle: circle = 'N/A'
        
        aadhaar = record.get('id', 'N/A')
        email = record.get('email', 'None')
        if email == 'None' or not email: email = 'N/A'
        
        address = record.get('address', 'N/A')
        clean_address = address.replace('!', ', ').strip(', ') if address != 'N/A' else 'N/A'

        # The Elite Report Format (Wrapped in <pre> for Copy Code button)
        report = (
            "<pre>"
            "NUMBER LOOKUP REPORT\n\n"
            "✦⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯✦\n"
            f"👤 Number       : {mobile}\n"
            "📊 Total Records: 1\n"
            "✦⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯✦\n\n"
            "Record #1\n"
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
        
        # Edit the message with the final report and buttons
        bot.edit_message_text(report, message.chat.id, msg.message_id, parse_mode='HTML', reply_markup=get_menu())
        
    else:
        bot.edit_message_text(
            text=f"🔴 <b>DATA NOT FOUND:</b> <code>{mobile}</code>\n\n<i>No records found in the database.</i>",
            chat_id=message.chat.id,
            message_id=msg.message_id,
            parse_mode='HTML',
            reply_markup=get_menu()
        )

# --- INVALID INPUT HANDLER ---
@bot.message_handler(func=lambda message: True)
def invalid_input(message):
    bot.reply_to(message, "❌ <b>ERROR:</b> Invalid format. Please send a valid 10-digit mobile number.", parse_mode='HTML')

# --- DUMMY WEB SERVER (Render ke liye) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Osama OSINT Bot is running successfully!"

def run_web():
    # Render humein PORT environment variable deta hai
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Web server ko background thread mein chalayein
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    print("🤖 Osama Elite Bot is running...")
    bot.polling(none_stop=True)
