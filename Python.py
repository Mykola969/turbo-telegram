import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_PASSWORD = os.getenv("BOT_PASSWORD", "15031995Sinok")

authorized_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 Введите пароль для доступа к боту:"
    )

async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id in authorized_users:
        return

    if text == BOT_PASSWORD:
        authorized_users.add(user_id)
        keyboard = ReplyKeyboardMarkup(
            [["📊 Сигнал", "⚙️ Настройки"]],
            resize_keyboard=True
        )
        await update.message.reply_text(
            "✅ Доступ разрешён. Выберите действие:",
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text("❌ Неверный пароль. Попробуйте ещё раз.")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in authorized_users:
        await update.message.reply_text("⛔ Сначала введите пароль.")
        return

    text = update.message.text

    if text == "📊 Сигнал":
        await update.message.reply_text(
            "📈 Сигнал:\n\n"
            "Пара: EUR/USD\n"
            "Направление: BUY\n"
            "Таймфрейм: 1M\n"
            "Вероятность: 82%\n\n"
            "Стратегии:\n"
            "✔ EMA + RSI\n"
            "✔ Bollinger Bands\n"
            "✔ Price Action"
        )

    elif text == "⚙️ Настройки":
        await update.message.reply_text(
            "⚙️ Настройки скоро будут добавлены."
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_password))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu))

    print("🤖 Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
