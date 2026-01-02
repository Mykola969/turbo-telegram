import telebot
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🤖 Бот запущен!\n\nЕсли ты это видишь — бот работает ✅"
    )

bot.infinity_polling()
