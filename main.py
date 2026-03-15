import os
import telebot
import google.generativeai as genai

TOKEN = os.getenv('TELEGRAM_TOKEN')
API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TOKEN)

# Ин сатр хатои Webhook-ро автоматӣ тоза мекунад
bot.remove_webhook()

@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        res = model.generate_content(f"Ту ёрдамчии тоҷик ҳастӣ: {message.text}")
        bot.reply_to(message, res.text)
    except Exception as e:
        print(f"Хатогӣ: {e}")

bot.infinity_polling()
