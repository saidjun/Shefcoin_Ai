import os
import threading
import telebot
import google.generativeai as genai
from flask import Flask, render_template

# Калидҳои ту
TOKEN = '8780142915:AAE7lMwsS4O1S5V2MhOmn2JQ3Nf_iZDifcQ'
API_KEY = 'AIzaSyDMA9WC1p8CwG3ABNcfPHLSpM_5AtAAFjk'

bot = telebot.TeleBot(TOKEN)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)

# --- WEB SITE ---
@app.route('/')
def index():
    return render_template('index.html')

# --- МЕНЮҲОИ ТЕЛЕГРАМ ---

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('👤 Профил', '💰 Баланс', '👨‍💻 IT Expert')
    markup.add('🔐 Амният', '🎧 Дастгирӣ')
    bot.reply_to(message, "📱 Хуш омадед ба Shefcoin Super-App!\nТугмаеро интихоб кунед ё ба AI савол диҳед:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '👤 Профил' or message.text == '/profile')
def profile(message):
    text = (f"👤 **Кабинети шахсӣ**\n\n🆔 ID: `{message.from_user.id}`\n👤 Ном: {message.from_user.first_name}\n💰 Баланс: 0.00 TJS\n🌟 Статус: Корбар")
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '💰 Баланс' or message.text == '/top_up')
def balance(message):
    bot.reply_to(message, "💰 **Пур кардани баланс**\n\nБарои гузаронидани маблағ ба @saidjun нависед.")

@bot.message_handler(func=lambda message: message.text == '👨‍💻 IT Expert' or message.text == '/it_expert')
def it_expert(message):
    bot.reply_to(message, "👨‍💻 **IT Expert AI**\n\nМан тайёрам ба саволҳои барномасозии шумо ҷавоб диҳам. Нависед!")

@bot.message_handler(func=lambda message: message.text == '🔐 Амният')
def security(message):
    bot.reply_to(message, "🔐 **Амният**\n\nҲисоби шумо таҳти ҳимояи Shefcoin AI мебошад.")

@bot.message_handler(func=lambda message: message.text == '🎧 Дастгирӣ')
def support(message):
    bot.reply_to(message, "🎧 **Маркази дастгирӣ**\n\nАдмин: @Shumakher03")

# ҶАВОБИ AI БА ПАЁМҲОИ ОДДӢ
@bot.message_handler(func=lambda message: True)
def ai_response(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "❌ Хатогӣ дар AI. Лутфан API Key-ро санҷед.")

def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
