import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.filters import Command

TOKEN = "ВСТАВЬ_СВОЙ_BOT_TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher()

users = {}

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "pair": None,
            "expiration": None
        }
    return users[uid]

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Торговля", callback_data="trade")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
        [InlineKeyboardButton(text="📈 Статистика", callback_data="stats")]
    ])

def trade_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💱 Валютная пара", callback_data="pairs")],
        [InlineKeyboardButton(text="⏱ Экспирация", callback_data="expiration")],
        [InlineKeyboardButton(text="🔄 Получить сигнал", callback_data="signal")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])

def pair_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Обычные пары", callback_data="regular_pairs")],
        [InlineKeyboardButton(text="🌙 OTC пары", callback_data="otc_pairs")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="trade")]
    ])

regular_pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"]
otc_pairs = ["EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC"]

def pairs_keyboard(pairs):
    kb = []
    for p in pairs:
        kb.append([InlineKeyboardButton(text=p, callback_data=f"pair_{p}")])
    kb.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="pairs")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def expiration_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="30 сек", callback_data="exp_30")],
        [InlineKeyboardButton(text="1 мин", callback_data="exp_60")],
        [InlineKeyboardButton(text="2 мин", callback_data="exp_120")],
        [InlineKeyboardButton(text="5 мин", callback_data="exp_300")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="trade")]
    ])

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("🤖 Бот запущен", reply_markup=main_menu())

@dp.callback_query(F.data == "trade")
async def trade(call: CallbackQuery):
    await call.message.edit_text("📊 Торговля", reply_markup=trade_menu())

@dp.callback_query(F.data == "pairs")
async def pairs(call: CallbackQuery):
    await call.message.edit_text("💱 Выбор валютной пары", reply_markup=pair_menu())

@dp.callback_query(F.data == "regular_pairs")
async def reg(call: CallbackQuery):
    await call.message.edit_text("🌍 Обычные пары", reply_markup=pairs_keyboard(regular_pairs))

@dp.callback_query(F.data == "otc_pairs")
async def otc(call: CallbackQuery):
    await call.message.edit_text("🌙 OTC пары", reply_markup=pairs_keyboard(otc_pairs))

@dp.callback_query(F.data.startswith("pair_"))
async def set_pair(call: CallbackQuery):
    user = get_user(call.from_user.id)
    user["pair"] = call.data.replace("pair_", "")
    await call.answer(f"Пара выбрана: {user['pair']}")

@dp.callback_query(F.data == "expiration")
async def exp(call: CallbackQuery):
    await call.message.edit_text("⏱ Выбор экспирации", reply_markup=expiration_menu())

@dp.callback_query(F.data.startswith("exp_"))
async def set_exp(call: CallbackQuery):
    user = get_user(call.from_user.id)
    user["expiration"] = int(call.data.replace("exp_", ""))
    await call.answer(f"Экспирация {user['expiration']} сек")

@dp.callback_query(F.data == "signal")
async def signal(call: CallbackQuery):
    user = get_user(call.from_user.id)

    if not user["pair"] or not user["expiration"]:
        await call.answer("❗ Выбери пару и экспирацию", show_alert=True)
        return

    await call.message.answer(
        f"""📊 СИГНАЛ

Пара: {user['pair']}
Экспирация: {user['expiration']} сек

📈 Направление: CALL
📊 Подтверждения: 4/5
🔍 EMA + RSI + BB + PA
""",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Обновить сигнал", callback_data="signal")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="trade")]
        ])
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
