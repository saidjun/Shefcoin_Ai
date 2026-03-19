import telebot
import os
import time
import requests
from flask import Flask
from threading import Thread
from telebot import types

# 👑 CONFIG
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = 6967256070
bot = telebot.TeleBot(TOKEN)
app = Flask('')

# 📊 DATABASE (Имитатсияи касбӣ)
users_db = {} # Дар лоиҳаи калон инро ба SQL пайваст мекунем

@app.route('/')
def home():
    return "<h1>Shefcoin AI Super-App is Running!</h1>"

def run():
    app.run(host='0.0.0.0', port=8080)

# 🛠 МЕНЮИ АСОСӢ (ГРАФИКАИ БАЛАНД)
def main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=3)
    btns = [
        types.InlineKeyboardButton("🏦 Сандуқ", callback_data="wallet"),
        types.InlineKeyboardButton("🛰 VPN/Proxy", callback_data="vpn"),
        types.InlineKeyboardButton("🏗 Конструктор", callback_data="constructor"),
        types.InlineKeyboardButton("📊 Биржа", callback_data="exchange"),
        types.InlineKeyboardButton("👤 Профил", callback_data="profile"),
        types.InlineKeyboardButton("🎁 Бонус", callback_data="bonus"),
        types.InlineKeyboardButton("🛡 Амният", callback_data="security"),
        types.InlineKeyboardButton("📞 Дастгирӣ", callback_data="support"),
        types.InlineKeyboardButton("⚙️ Настройка", callback_data="settings")
    ]
    markup.add(*btns)
    markup.add(types.InlineKeyboardButton("👑 ПАНЕЛИ АДМИН", callback_data="admin_panel"))
    return markup
# 🛰 МОДУЛИ VPN
@bot.callback_query_handler(func=lambda call: call.data == "vpn")
def vpn_module(call):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("⚡ Гирифтани V2Ray", callback_data="get_v2ray"),
        types.InlineKeyboardButton("🌍 Proxy (MTProto)", callback_data="get_proxy"),
        types.InlineKeyboardButton("🔙 Ба қафо", callback_data="back_to_main")
    )
    bot.edit_message_text("🛰 **SHEFCOIN VPN SERVICE**\n\nМо пайвасти бехатарро таъмин мекунем.", 
                          call.message.chat.id, call.message.message_id, reply_markup=kb, parse_mode="Markdown")

# 🏗 МОДУЛИ КОНСТРУКТОР
@bot.callback_query_handler(func=lambda call: call.data == "constructor")
def constructor_module(call):
    bot.send_message(call.message.chat.id, "🛠 **КОНСТРУКТОРИ БОТҲО**\n\nТокени худро фиристед:")
    bot.register_next_step_handler(call.message, build_bot_process)

def build_bot_process(message):
    # Логикаи тафтиши токен ва сохтани папкаҳо дар сервер
    token = message.text
    bot.send_message(message.chat.id, f"✅ **Токен қабул шуд!**\n\nСохтмони бот оғоз ёфт...")
# --- МОДУЛИ БИРЖА (EXCHANGE) ---
@bot.callback_query_handler(func=lambda call: call.data == "exchange")
def exchange_page(call):
    # Нархҳои сунъӣ (ё метавон бо API пайваст кард)
    btc_price = 68450.25
    eth_price = 3540.10
    ton_price = 7.24
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📈 Харид", callback_data="buy_crypto"),
        types.InlineKeyboardButton("📉 Фурӯш", callback_data="sell_crypto"),
        types.InlineKeyboardButton("🔄 Навсозӣ", callback_data="exchange"),
        types.InlineKeyboardButton("🔙 Ба қафо", callback_data="back_to_main")
    )
    
    text = (
        "📊 **БИРЖАИ SHEFCOIN AI**\n\n"
        f"🟠 **Bitcoin:** ${btc_price}\n"
        f"🔵 **Ethereum:** ${eth_price}\n"
        f"💎 **TON:** ${ton_price}\n\n"
        "💰 Баланси шумо: 0.00 TJS\n"
        "⚡ Курсҳо ҳар 5 дақиқа нав мешаванд."
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

# --- МОДУЛИ БОНУС (СИСТЕМАИ ТАҲРИКӢ) ---
@bot.callback_query_handler(func=lambda call: call.data == "bonus")
def bonus_system(call):
    bot.answer_callback_query(call.id, "🎁 Шумо бонуси ҳаррӯзаро гирифтед: 0.50 TJS")
    bot.send_message(call.message.chat.id, "🎉 **Табрик!** Ба суратҳисоби шумо 0.50 TJS илова шуд.")

# --- МОДУЛИ АМНИЯТ (SECURITY) ---
@bot.callback_query_handler(func=lambda call: call.data == "security")
def security_module(call):
    text = (
        "🛡 **МАРКАЗИ АМНИЯТ:**\n\n"
        "✅ Шифргузории AES-256 фаъол аст.\n"
        "✅ Пайвасти VPN: Ҳимояшуда.\n"
        "✅ Дузинагӣ (2FA): Тавсия мешавад.\n\n"
        "Шумо дар ҳолати бехатар ҳастед."
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, 
                          reply_markup=main_keyboard(), parse_mode="Markdown")
# --- ПАНЕЛИ АДМИН (ADMIN PANEL) ---
@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def admin_main(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Шумо ҳуқуқи админ надоред!")
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Фиристодани хабар (Рассылка)", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("👥 Омори корбарон", callback_data="admin_stats"),
        types.InlineKeyboardButton("💰 Додани пул (Give)", callback_data="admin_give"),
        types.InlineKeyboardButton("🔙 Ба қафо", callback_data="back_to_main")
    )
    bot.edit_message_text("👑 **ПАНЕЛИ ШЕФ (ADMIN):**\n\nҲамаи фишангҳои идора дар инҷост.", 
                          call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
def admin_stats(call):
    # Дар инҷо баъдтар логикаи ҳисоб кардани одамонро аз база илова мекунем
    bot.send_message(call.message.chat.id, "👥 **ОМОР:**\n\nКорбарони умумӣ: 1\nБотҳои сохташуда: 0\nФоидаи имрӯза: 0 TJS")
# --- МОДУЛИ РЕФЕРАЛӢ (REFERRAL SYSTEM) ---
@bot.callback_query_handler(func=lambda call: call.data == "referral")
def referral_system(call):
    reflink = f"https://t.me/{(bot.get_me()).username}?start={call.from_user.id}"
    text = (
        "👥 **ПРОГРАММАИ РЕФЕРАЛӢ:**\n\n"
        "Дӯстони худро даъват кунед ва 10% аз харидҳои онҳоро гиред!\n\n"
        f"🔗 Пайванди шумо:\n`{reflink}`\n\n"
        "Сатҳи шумо: Бронза 🥉\n"
        "Даъватшудагон: 0 одам"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, 
                          reply_markup=main_keyboard(), parse_mode="Markdown")

# --- МОДУЛИ МАҒОЗА (SHOP MODULE) ---
@bot.callback_query_handler(func=lambda call: call.data == "shop")
def shop_module(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🤖 Харидани Боти Тайёр", callback_data="buy_bot_ready"),
        types.InlineKeyboardButton("🔑 Харидани Ключи VPN", callback_data="buy_vpn_key"),
        types.InlineKeyboardButton("🔙 Ба қафо", callback_data="back_to_main")
    )
    bot.edit_message_text("🛒 **МАҒОЗАИ SHEFCOIN:**\n\nБеҳтарин хизматрасониҳои автоматиро интихоб кунед.", 
                          call.message.chat.id, call.message.message_id, reply_markup=markup)

# --- ФУНКСИЯИ БА ҚАФО (BACK TO MAIN) ---
@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_home(call):
    bot.edit_message_text(f"💎 **Хуш омадед, Шеф {call.from_user.first_name}!**\n\nМенюи асосӣ омода аст:", 
                          call.message.chat.id, call.message.message_id, reply_markup=main_keyboard())
# --- ПАНЕЛИ АДМИН (ADMIN PANEL) ---
@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def admin_main(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Шумо ҳуқуқи админ надоред!")
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Фиристодани хабар (Рассылка)", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("👥 Омори корбарон", callback_data="admin_stats"),
        types.InlineKeyboardButton("💰 Додани пул (Give)", callback_data="admin_give"),
        types.InlineKeyboardButton("🔙 Ба қафо", callback_data="back_to_main")
    )
    bot.edit_message_text("👑 **ПАНЕЛИ ШЕФ (ADMIN):**\n\nҲамаи фишангҳои идора дар инҷост.", 
                          call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
def admin_stats(call):
    # Дар инҷо баъдтар логикаи ҳисоб кардани одамонро аз база илова мекунем
    bot.send_message(call.message.chat.id, "👥 **ОМОР:**\n\nКорбарони умумӣ: 1\nБотҳои сохташуда: 0\nФоидаи имрӯза: 0 TJS")
