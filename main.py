import os
import telebot
import google.generativeai as genai

# Ин маълумотҳоро Render баъдтар худаш меёбад
TOKEN = os.getenv('TELEGRAM_TOKEN')
API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        # Промти махсуси ту
        prompt = f"Ту ёрдамчии Shefcoin AI ҳастӣ. Ба забони тоҷикӣ бо смайликҳо ҷавоб деҳ: {message.text}"
        response = model.generate_content(prompt)
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Хатогӣ: {e}")
        bot.reply_to(message, "Бубахшед, ҳозир ҷавоб дода наметавонам.")

if __name__ == "__main__":
    bot.infinity_polling()
