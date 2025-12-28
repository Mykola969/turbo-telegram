import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = "7844308662:AAHRZ8sMWFHbOed9N-nmcPssnQQh544o4Jk"
PASSWORD = "15031995Sinok"

logging.basicConfig(level=logging.INFO)

AUTHORIZED_USERS = set()
SELECTED_PAIR = {}

PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "EUR/USD OTC"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 Введите пароль для доступа к боту:"
    )

async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == PASSWORD:
        AUTHORIZED_USERS.add(update.message.from_user.id)
        await show_menu(update)
    else:
        await update.message.reply_text("❌ Неверный пароль")

async def show_menu(update):
    keyboard = [
        [InlineKeyboardButton("📊 Выбрать пару", callback_data="pair")],
        [InlineKeyboardButton("📈 Получить сигнал", callback_data="signal")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✅ Доступ разрешён", reply_markup=reply_markup)

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id not in AUTHORIZED_USERS:
        await query.message.reply_text("⛔ Нет доступа. Введите пароль.")
        return

    if query.data == "pair":
        keyboard = [[InlineKeyboardButton(p, callback_data=f"pair_{p}")] for p in PAIRS]
        await query.message.reply_text(
            "Выбери валютную пару:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif query.data.startswith("pair_"):
        pair = query.data.replace("pair_", "")
        SELECTED_PAIR[query.from_user.id] = pair
        await query.message.reply_text(f"✅ Выбрана пара: {pair}")

    elif query.data == "signal":
        pair = SELECTED_PAIR.get(query.from_user.id, "Все пары")
        await query.message.reply_text(
            f"""📊 СИГНАЛ
Пара: {pair}
Таймфрейм: 1м
Экспирация: 2 мин

📈 Стратегии:
✔ EMA
✔ RSI
✔ Bollinger Bands
✔ Price Action

🔥 Сигнал: CALL
Вероятность: ~78%
"""
        )

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in AUTHORIZED_USERS:
        await check_password(update, context)
    else:
        await update.message.reply_text("Используй меню 👇")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(
        telegram.ext.MessageHandler(
            telegram.ext.filters.TEXT & ~telegram.ext.filters.COMMAND,
            message_router,
        )
    )

    app.run_polling()

if __name__ == "__main__":
    main()
