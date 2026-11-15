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
# 👇 NAYA API URL 👇
# =====================================================================
API_BASE_URL = "https://api.darknetwork.site/index.php?api=hi_tek&key=key_DarkApiX444&search={}"
# =====================================================================

bot = telebot.TeleBot(BOT_TOKEN)

# =====================================================================
# 👇 YAHAN APNA NUMBER ADD KAREIN 👇
# =====================================================================
# Apna number double quotes ("") ke andar dalein. 
# Agar 10 digit ka mobile hai toh aise: "7991536322"
# Agar 12 digit ka aadhaar hai toh aise: "723229708091"
PROTECTED_NUMBERS = ["9621303160", "7991536322", "8604302624", "6204473620"]  
# =====================================================================

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

    # 🚫 BLACKLIST CHECK (Yahan aapka number check hoga)
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
        # SPAM FIX: Hum sirf pehla record (records[0]) uthayenge
        record = records[0]
        
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
# Dhyan rakhein: Chat ID ko string mein convert karna zaroori hai
YOUR_CHAT_ID = str(os.environ.get('CHAT_ID'))

# =====================================================================
# 👇 NAYA API URL 👇
# =====================================================================
API_BASE_URL = "https://api.darknetwork.site/index.php?api=hi_tek&key=key_DarkApiX444&search={}"
# =====================================================================

bot = telebot.TeleBot(BOT_TOKEN)

# =====================================================================
# 👇 VIP ACCESS CONTROL (Authorized Users) 👇
# =====================================================================
ALLOWED_USERS = [
    YOUR_CHAT_ID,       # Aap (Owner) - Ise kabhi mat hatana
    "8707785706",       # Authorized User 1
    "8898567917",       # Authorized User 2
    "5704555109",       # Authorized User 3
    "6700078527"        # Authorized User 4
]

# Numbers jo database se protect karne hain (Aapka aur aapke doston ka)
PROTECTED_NUMBERS = ["9621303160", "7991536322", "8604302624", "6204473620"]

# --- CHECK PERMISSION FUNCTION ---
def is_authorized(user_id):
    # Agar user owner hai ya allowed list mein hai
    if str(user_id) == YOUR_CHAT_ID or str(user_id) in ALLOWED_USERS:
        return True
    return False

# --- MENU (CONTACT DEVELOPER BUTTON) ---
def get_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_dev = types.InlineKeyboardButton("👨‍💻 Contact Developer (Osama)", url=f"tg://user?id={YOUR_CHAT_ID}")
    markup.add(btn_dev)
    return markup

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    # 🚫 CHECK ACCESS
    if not is_authorized(user_id):
        bot.reply_to(
            message, 
            "🚫 <b>ACCESS DENIED</b>\n\n"
            "You do not have the required clearance to access this system.\n\n"
            "🔒 <i>This bot is restricted to authorized personnel only.</i>\n"
            "👉 <b>To request access, please contact Osama via the button below.</b>", 
            parse_mode='HTML', 
            reply_markup=get_menu()
        )
        return

    text = (
        "🟢 <b>OSAMA OSINT ENGINE v8.0</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Send me any <b>10-digit Mobile Number</b> or <b>12-digit Aadhaar Number</b>, and I will provide you with all the details.\n\n"
        "⚠️ <i>All queries are logged. Use strictly for educational purposes.</i>"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=get_menu())

# --- ADMIN COMMANDS (Kisi ko access dene ke liye) ---
@bot.message_handler(commands=['allow'])
def allow_user(message):
    if str(message.from_user.id) != YOUR_CHAT_ID:
        return # Sirf owner kar sakta hai
        
    try:
        new_id = message.text.split()[1]
        if new_id not in ALLOWED_USERS:
            ALLOWED_USERS.append(new_id)
            bot.reply_to(message, f"✅ User ID <code>{new_id}</code> has been granted VIP Access.", parse_mode='HTML')
        else:
            bot.reply_to(message, "⚠️ User is already in the VIP list.")
    except IndexError:
        bot.reply_to(message, "❌ <b>Format:</b> <code>/allow 123456789</code>", parse_mode='HTML')

@bot.message_handler(commands=['remove'])
def remove_user(message):
    if str(message.from_user.id) != YOUR_CHAT_ID:
        return
        
    try:
        remove_id = message.text.split()[1]
        if remove_id in ALLOWED_USERS and remove_id != YOUR_CHAT_ID:
            ALLOWED_USERS.remove(remove_id)
            bot.reply_to(message, f"✅ User ID <code>{remove_id}</code> has been removed from VIP Access.", parse_mode='HTML')
        else:
            bot.reply_to(message, "⚠️ User not found or cannot remove Owner.")
    except IndexError:
        bot.reply_to(message, "❌ <b>Format:</b> <code>/remove 123456789</code>", parse_mode='HTML')


# --- SCANNER HANDLER ---
@bot.message_handler(func=lambda message: message.text.isdigit() and len(message.text) in [10, 12])
def handle_scan(message):
    user_id = message.from_user.id
    
    # 🚫 CHECK ACCESS
    if not is_authorized(user_id):
        bot.reply_to(
            message, 
            "🚫 <b>ACCESS DENIED</b>\n\n"
            "Your identity is not recognized.\n"
            "👉 <b>Contact Osama to get VIP access and use this bot.</b>", 
            parse_mode='HTML', 
            reply_markup=get_menu()
        )
        return

    query = message.text
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    query_type = "MOBILE" if len(query) == 10 else "AADHAAR"

    # 🔥 ADMIN LOGGING SYSTEM
    if str(user_id) != YOUR_CHAT_ID:
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
YOUR_CHAT_ID = str(os.environ.get('CHAT_ID'))

API_BASE_URL = "https://api.darknetwork.site/index.php?api=hi_tek&key=key_DarkApiX444&search={}"

bot = telebot.TeleBot(BOT_TOKEN)

# =====================================================================
# 👇 VIP ACCESS CONTROL (Only IDs required) 👇
# =====================================================================
ALLOWED_USERS = [
    YOUR_CHAT_ID,       # Aap (Owner)
    "8707785706",       # User 1
    "8898567917",       # User 2
    "6700078527",       # User 3
    "5704555109",       # User 4
    "901112667",        # User 5 
    "8659201578"        # User 6
]

# Numbers jo database se protect karne hain
PROTECTED_NUMBERS = ["9621303160", "7991536322", "8604302624", "6204473620"]

# --- CHECK PERMISSION FUNCTION ---
def is_authorized(user_id):
    return str(user_id) in ALLOWED_USERS or str(user_id) == YOUR_CHAT_ID

# --- MENU (CONTACT DEVELOPER BUTTON) ---
def get_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_dev = types.InlineKeyboardButton("👨‍💻 Contact Developer (Osama)", url=f"tg://user?id={YOUR_CHAT_ID}")
    markup.add(btn_dev)
    return markup

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if not is_authorized(user_id):
        bot.reply_to(
            message, 
            "🚫 <b>ACCESS DENIED</b>\n\n"
            "You do not have the required clearance to access this system.\n\n"
            "🔒 <i>This bot is restricted to authorized personnel only.</i>\n"
            "👉 <b>To request access, please contact Osama via the button below.</b>", 
            parse_mode='HTML', 
            reply_markup=get_menu()
        )
        return

    text = (
        "🟢 <b>OSAMA OSINT ENGINE v8.0</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Send me any <b>10-digit Mobile Number</b> or <b>12-digit Aadhaar Number</b>, and I will provide you with all the details.\n\n"
        "⚠️ <i>All queries are logged. Use strictly for educational purposes.</i>"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=get_menu())

# --- ADMIN COMMANDS (ADD/REMOVE/LIST USERS) ---
@bot.message_handler(commands=['allow'])
def allow_user(message):
    if str(message.from_user.id) != YOUR_CHAT_ID:
        return 
        
    try:
        new_id = message.text.split()[1]
        if new_id not in ALLOWED_USERS:
            ALLOWED_USERS.append(new_id)
            bot.reply_to(message, f"✅ User ID <code>{new_id}</code> has been granted VIP Access.", parse_mode='HTML')
        else:
            bot.reply_to(message, "⚠️ User is already in the VIP list.")
    except IndexError:
        bot.reply_to(message, "❌ <b>Format:</b> <code>/allow 123456789</code>", parse_mode='HTML')

@bot.message_handler(commands=['remove'])
def remove_user(message):
    if str(message.from_user.id) != YOUR_CHAT_ID:
        return
        
    try:
        remove_id = message.text.split()[1]
        if remove_id in ALLOWED_USERS and remove_id != YOUR_CHAT_ID:
            ALLOWED_USERS.remove(remove_id)
            bot.reply_to(message, f"✅ User ID <code>{remove_id}</code> has been removed from VIP Access.", parse_mode='HTML')
        else:
            bot.reply_to(message, "⚠️ User not found or cannot remove Owner.")
    except IndexError:
        bot.reply_to(message, "❌ <b>Format:</b> <code>/remove 123456789</code>", parse_mode='HTML')

@bot.message_handler(commands=['list_users', 'users'])
def list_allowed_users(message):
    if str(message.from_user.id) != YOUR_CHAT_ID:
        return
        
    response = "👑 <b>VIP ACCESS LIST</b> 👑\n"
    response += "━━━━━━━━━━━━━━━━━━━━━━\n"
    response += "<i>Fetching names from Telegram...</i>\n\n"
    
    msg = bot.reply_to(message, response, parse_mode='HTML')
    
    final_response = "👑 <b>VIP ACCESS LIST</b> 👑\n"
    final_response += "━━━━━━━━━━━━━━━━━━━━━━\n"
    
    for i, user_id in enumerate(ALLOWED_USERS, 1):
        role = " (👑 Owner)" if str(user_id) == YOUR_CHAT_ID else ""
        
        try:
            # Telegram API se naam nikalne ki koshish
            chat_info = bot.get_chat(user_id)
            user_name = chat_info.first_name
            if chat_info.last_name:
                user_name += f" {chat_info.last_name}"
        except Exception:
            # Agar user ne bot start nahi kiya ya ID galat hai
            user_name = "Unknown (Not started bot)"
            
        final_response += f"{i}. <b>{user_name}</b>\n"
        final_response += f"    🆔 <code>{user_id}</code>{role}\n"
            
    final_response += "━━━━━━━━━━━━━━━━━━━━━━\n"
    final_response += f"<b>Total Authorized Users:</b> {len(ALLOWED_USERS)}"
    
    # Pehle bheje gaye message ko update kar dein
    bot.edit_message_text(final_response, message.chat.id, msg.message_id, parse_mode='HTML')

# --- SCANNER HANDLER ---
@bot.message_handler(func=lambda message: message.text.isdigit() and len(message.text) in [10, 12])
def handle_scan(message):
    user_id = message.from_user.id
    
    if not is_authorized(user_id):
        bot.reply_to(
            message, 
            "🚫 <b>ACCESS DENIED</b>\n\n"
            "Your identity is not recognized.\n"
            "👉 <b>Contact Osama to get VIP access and use this bot.</b>", 
            parse_mode='HTML', 
            reply_markup=get_menu()
        )
        return

    query = message.text
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    query_type = "MOBILE" if len(query) == 10 else "AADHAAR"

    # 🔥 ADMIN LOGGING SYSTEM
    if str(user_id) != YOUR_CHAT_ID:
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
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        res = requests.get(API_BASE_URL.format(query), headers=headers, timeout=60)
        
        if res.status_code == 200:
            data = res.json()
            if data.get('status') == 'success' and 'data' in data:
                records = data['data']
    except Exception as e:
        print(f"API Error: {e}")
            
    if records:
        record = records[0]
        
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

        report = (
            "<pre>"
            "OSINT LOOKUP REPORT\n\n"
            "✦⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯✦\n"
            f"👤 Query        : {query}\n"
            f"📊 Type         : {query_type}\n"
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
        
        bot.edit_message_text(report, message.chat.id, msg.message_id, parse_mode='HTML', reply_markup=get_menu())
        
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
    if not is_authorized(message.from_user.id):
        bot.reply_to(
            message, 
            "🚫 <b>ACCESS DENIED</b>\n\n"
            "You do not have permission to use this bot.", 
            parse_mode='HTML',
            reply_markup=get_menu()
        )
        return
    bot.reply_to(message, "❌ <b>ERROR:</b> Invalid format. Please send a valid 10-digit Mobile or 12-digit Aadhaar.", parse_mode='HTML')

# --- DUMMY WEB SERVER (Render ke liye) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Osama OSINT Bot (Auto-Name Mode) is running successfully!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    print("🤖 Osama Elite Bot (Auto-Name Mode) is running...")
    bot.polling(none_stop=True)
