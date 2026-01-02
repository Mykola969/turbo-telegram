
import logging
import random
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ==== Настройки ====
TOKEN = "7741062103:AAF9xj8Er3WjSP1LUoSbxXPh90mINhkpy_M"
PASSWORD = "15031995Sinok"
AUTHORIZED_USERS = set()

# ==== Валютные пары ====
AVAILABLE_PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "BTC/USD", "AUD/JPY", "OTC/EURUSD", "OTC/GBPUSD"]
user_selected_pairs = {}

# ==== Состояние сигналов ====
signals_active = {}

# ==== Логгирование ====
logging.basicConfig(level=logging.INFO)

# ==== Генерация сигналов ====
STRATEGIES = ["EMA", "RSI", "Свечной анализ", "Price Action", "BB + RSI"]

def generate_fake_signal():
    # Симулируем выбор валютной пары и направления
    pair = random.choice(["EUR/USD", "GBP/USD", "USD/JPY", "BTC/USD", "AUD/JPY", "OTC/EURUSD", "OTC/GBPUSD"])
    direction = random.choice(["CALL", "PUT"])
    timeframes = ["30с", "1м", "2м"]
    timeframe = random.choice(timeframes)

    # Симулируем сработавшие стратегии
    confirmed_strategies = random.sample(STRATEGIES, k=random.randint(2, 5))
    signal_time = datetime.now().strftime("%H:%M:%S")

    return {
        "pair": pair,
        "direction": direction,
        "strategies": confirmed_strategies,
        "time": signal_time,
        "timeframe": timeframe,
        "confirmations": len(confirmed_strategies)
    }

async def signal_sender(app):
    while True:
        for user_id in signals_active:
            if signals_active.get(user_id, False):
                # Учитываем выбранную пару (если указана)
                selected_pair = user_selected_pairs.get(user_id, "ALL")
                signal = generate_fake_signal()

                if selected_pair != "ALL" and signal["pair"] != selected_pair:
                    continue  # пропускаем, если не та пара

                direction_text = "🟢 CALL (Покупка)" if signal['direction'] == "CALL" else "🔴 PUT (Продажа)"
                strategies_text = ''.join(f"✅ {s}\n" for s in signal['strategies'])
                
                message = f"""📡 <b>Сигнал на {signal['timeframe']} ({signal['pair']})</b>

📈 <b>Направление:</b> {direction_text}

🧠 <b>Стратегии сработали:</b>
{strategies_text}
⏱ <b>Время:</b> {signal['time']}
🔎 <b>Подтверждений:</b> {signal['confirmations']} из 5
"""
                try:
                    await app.bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")
                except Exception as e:
                    print(f"Ошибка отправки пользователю {user_id}: {e}")

        await asyncio.sleep(30)  # каждые 30 секунд

# ==== Команды ====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Введите пароль с помощью /login <пароль>")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❗ Используй: /login <пароль>")
        return
    if context.args[0] == PASSWORD:
        user_id = update.effective_user.id
        AUTHORIZED_USERS.add(user_id)
        await update.message.reply_text("✅ Успешный вход! Используй /start_signals для начала.")
    else:
        await update.message.reply_text("❌ Неверный пароль")

async def start_signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("🚫 Сначала войди с /login")
        return
    signals_active[user_id] = True
    await update.message.reply_text("🟢 Сигналы запущены.")
    await show_pair_menu(update, context)

async def stop_signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    signals_active[user_id] = False
    await update.message.reply_text("🔴 Сигналы остановлены.")

async def show_pair_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(pair, callback_data=pair)] for pair in AVAILABLE_PAIRS]
    keyboard.append([InlineKeyboardButton("Все пары", callback_data="ALL")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📊 Выберите валютную пару:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_selected_pairs[user_id] = query.data
    await query.edit_message_text(f"✅ Вы выбрали: {query.data}")

# ==== Обработка входящих ====
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("start_signals", start_signals))
    app.add_handler(CommandHandler("stop_signals", stop_signals))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Бот запущен.")
    
    # Инициализируем приложение
    await app.initialize()
    await app.start()
    
    # Запускаем отправщик сигналов в фоновом режиме
    asyncio.create_task(signal_sender(app))
    
    # Запускаем бота
    await app.updater.start_polling()
    
    # Ждем бесконечно
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
