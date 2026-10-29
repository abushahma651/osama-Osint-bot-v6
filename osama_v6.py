import telebot
import requests
import time
import json
from telebot import types

# --- CONFIGURATION ---
BOT_TOKEN = '9090123558:AAEE7JhFuxYPpUkQfLpcoc6EAAqeypMKn50'  # Yahan apna Bot Token dalein
YOUR_CHAT_ID = '8439527054' # Yahan apni Chat ID dalein (Numbers mein)

bot = telebot.TeleBot(BOT_TOKEN)

# API NODES
APIS = [
    {"name": "1.7B_ROWS_DB", "url": "https://tfqdeadlo-1-78bapi.hf.space/search?mobile={}"},
    {"name": "851M_ROWS_DB", "url": "https://tfqdeadlo-850crfastsearch.hf.space/search/{}"},
    {"name": "1.4B_ROWS_DB", "url": "https://tfqdeadlo-inddataapi.hf.space/search?mobile={}"}
]

# --- MENU (CONTACT DEVELOPER BUTTON) ---
def get_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    # Chat ID ke through direct chat open karne ka link
    btn_dev = types.InlineKeyboardButton("👨‍💻 Contact Developer (Osama)", url=f"tg://user?id={YOUR_CHAT_ID}")
    markup.add(btn_dev)
    return markup

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (
        "🟢 <b>OSAMA OSINT CORE v6.0</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "> System Status: <code>ONLINE</code>\n"
        "> Access Level:  <code>ROOT</code>\n"
        "> Encryption:   <code>AES-256</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send any 10-digit mobile number to fetch the <b>Raw JSON Dump</b> from the 3 linked databases.\n\n"
        "<i>⚠️ All queries are logged. Use strictly for educational purposes.</i>"
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=get_menu())

# --- SCANNER HANDLER ---
@bot.message_handler(func=lambda message: message.text.isdigit() and len(message.text) == 10)
def handle_scan(message):
    mobile = message.text
    msg = bot.send_message(message.chat.id, f"⚡ <b>TARGET:</b> <code>{mobile}</code>\n\n<code>[■□□□□□□□□□] INITIALIZING...</code>", parse_mode='HTML')
    
    # Premium Loading Sequence
    stages = [
        "> [■■■□□□□□□□] ROUTING VIA TOR...",
        "> [■■■■■□□□□□] BYPASSING FIREWALLS...",
        "> [■■■■■■■■□□] QUERYING 3 NODES...",
        "> [■■■■■■■■■■] EXTRACTING RAW DATA..."
    ]
    
    for stage in stages:
        time.sleep(0.8)
        bot.edit_message_text(f"⚡ <b>TARGET:</b> <code>{mobile}</code>\n\n<code>{stage}</code>", message.chat.id, msg.message_id, parse_mode='HTML')
        
    # Fetching Data
    found_any = False
    final_text = f"🟢 <b>DATA ACQUIRED:</b> <code>{mobile}</code>\n"
    final_text += "<i>Raw server responses below:</i>\n\n"
    
    for api in APIS:
        try:
            res = requests.get(api["url"].format(mobile), timeout=10)
            data = res.json()
            
            record = None
            if data and 'data' in data and data['data']:
                record = data['data']
                if isinstance(record, list): record = record[0]
            elif data and data.get('mobile'):
                record = data
                
            if record and record.get('mobile'):
                found_any = True
                
                # JSON ko clean format mein dump karna
                json_formatted = json.dumps(record, indent=2)
                
                final_text += f"📡 <b>[ {api['name']} ]</b>\n"
                # <pre> tag Telegram mein black terminal box bana deta hai
                final_text += f"<pre>{json_formatted}</pre>\n\n"
                
        except Exception:
            pass
            
    if found_any:
        final_text += "━━━━━━━━━━━━━━━━━━━━━━\n"
        final_text += "⚠️ <i>Trace complete. Data logged.</i>"
        bot.edit_message_text(final_text, message.chat.id, msg.message_id, parse_mode='HTML', reply_markup=get_menu())
    else:
        bot.edit_message_text(
            text=f"🔴 <b>TARGET NOT FOUND:</b> <code>{mobile}</code>\n\n<i>No records found in any database.</i>",
            chat_id=message.chat.id,
            message_id=msg.message_id,
            parse_mode='HTML',
            reply_markup=get_menu()
        )

# --- INVALID INPUT HANDLER ---
@bot.message_handler(func=lambda message: True)
def invalid_input(message):
    bot.reply_to(message, "❌ <b>ERROR:</b> Invalid format. Please send a 10-digit mobile number.", parse_mode='HTML')

print("🤖 Osama JSON Bot v6.0 is running...")
bot.polling()
