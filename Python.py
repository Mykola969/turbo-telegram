import telebot
from telebot import types
import pandas as pd
import random
from datetime import datetime
import matplotlib.pyplot as plt
import io

# ----------------- НАСТРОЙКИ -----------------
TOKEN = '7844308662:AAHRZ8sMWFHbOed9N-nmcPssnQQh544o4Jk'  # готовый токен бота
bot = telebot.TeleBot(TOKEN)
PASSWORD = '15031995Sinok'

pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD', 'OTC']
expirations = ['30с', '1м', '2м', '5м']
indicators = ['EMA','RSI','Свечной анализ','Bollinger Bands','Price Action','MACD','Stochastic']

user_sessions = {}
signal_history = []

# ----------------- LOGIN -----------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Введите пароль:")
    bot.register_next_step_handler(message, check_password)

def check_password(message):
    if message.text == PASSWORD:
        user_sessions[message.chat.id] = {'pair':'Все пары','exp':'1м','type':'Все'}
        show_main_menu(message)
    else:
        bot.send_message(message.chat.id, "Неверный пароль. Попробуйте снова:")
        bot.register_next_step_handler(message, check_password)

# ----------------- МЕНЮ -----------------
def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Выбрать валютную пару', 'Тип сигналов')
    markup.row('Время экспирации', 'Обновить сигнал')
    markup.row('Обновить VIP/Сильный сигнал')
    markup.row('История', 'Статистика')
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def menu_handler(message):
    chat_id = message.chat.id
    text = message.text

    if text == 'Выбрать валютную пару':
        choose_pair(chat_id)
    elif text == 'Тип сигналов':
        choose_signal_type(chat_id)
    elif text == 'Время экспирации':
        choose_expiration(chat_id)
    elif text == 'Обновить сигнал':
        send_signal(chat_id)
    elif text == 'Обновить VIP/Сильный сигнал':
        send_signal(chat_id, only_strong=True)
    elif text == 'История':
        show_history(chat_id)
    elif text == 'Статистика':
        show_stats(chat_id)
    else:
        bot.send_message(chat_id, "Выберите действие из меню.")

# ----------------- ВЫБОР ВАЛЮТНОЙ ПАРЫ -----------------
def choose_pair(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for p in pairs:
        markup.add(p)
    msg = bot.send_message(chat_id, "Выберите валютную пару:", reply_markup=markup)
    bot.register_next_step_handler(msg, set_pair)

def set_pair(message):
    chat_id = message.chat.id
    user_sessions[chat_id]['pair'] = message.text
    bot.send_message(chat_id, f"Выбрана пара: {message.text}")
    show_main_menu(message)

# ----------------- ВЫБОР ТИПА СИГНАЛОВ -----------------
def choose_signal_type(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Все сигналы', 'Сильный сигнал', 'VIP сигнал')
    msg = bot.send_message(chat_id, "Выберите тип сигналов:", reply_markup=markup)
    bot.register_next_step_handler(msg, set_signal_type)

def set_signal_type(message):
    chat_id = message.chat.id
    user_sessions[chat_id]['type'] = message.text
    bot.send_message(chat_id, f"Выбран тип сигналов: {message.text}")
    show_main_menu(message)

# ----------------- ВЫБОР ВРЕМЕНИ ЭКСПИРАЦИИ -----------------
def choose_expiration(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for t in expirations:
        markup.add(t)
    msg = bot.send_message(chat_id, "Выберите время экспирации:", reply_markup=markup)
    bot.register_next_step_handler(msg, set_expiration)

def set_expiration(message):
    chat_id = message.chat.id
    user_sessions[chat_id]['exp'] = message.text
    bot.send_message(chat_id, f"Выбрано время экспирации: {message.text}")
    show_main_menu(message)

# ----------------- СИМУЛЯЦИЯ ЦЕН -----------------
def simulate_prices(length=50):
    price = 1.0
    prices = []
    for _ in range(length):
        price += random.uniform(-0.002,0.002)
        prices.append(round(price,5))
    return prices

# ----------------- ГРАФИК С ПОСЛЕДНИМ СИГНАЛОМ -----------------
def plot_signal(prices, buy_indices, sell_indices):
    df = pd.DataFrame(prices, columns=['Close'])
    df['EMA'] = df['Close'].rolling(20).mean()
    df['BB_HI'] = df['Close'].rolling(20).max()
    df['BB_LOW'] = df['Close'].rolling(20).min()

    plt.figure(figsize=(6,3))
    plt.plot(df['Close'], label='Close', color='blue')
    plt.plot(df['EMA'], label='EMA20', color='orange')
    plt.plot(df['BB_HI'], label='Bollinger High', color='green')
    plt.plot(df['BB_LOW'], label='Bollinger Low', color='red')

    if buy_indices: plt.scatter(buy_indices[:-1], [df['Close'][i] for i in buy_indices[:-1]], color='green', marker='^', s=50, label='BUY')
    if sell_indices: plt.scatter(sell_indices[:-1], [df['Close'][i] for i in sell_indices[:-1]], color='red', marker='v', s=50, label='SELL')

    if buy_indices: plt.scatter(buy_indices[-1], df['Close'][buy_indices[-1]], color='lime', marker='^', s=150, label='LAST BUY')
    if sell_indices: plt.scatter(sell_indices[-1], df['Close'][sell_indices[-1]], color='magenta', marker='v', s=150, label='LAST SELL')

    plt.legend(loc='upper left')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

# ----------------- ГЕНЕРАЦИЯ СИГНАЛА -----------------
def send_signal(chat_id, only_strong=False):
    pair = user_sessions[chat_id].get('pair','Все пары')
    exp = user_sessions[chat_id].get('exp','1м')
    signal_type = user_sessions[chat_id].get('type','Все')

    prices = simulate_prices()
    latest_price = prices[-1]

    buy_indices = []
    sell_indices = []
    confirmed = 0
    direction_votes = []

    for i in range(len(prices)):
        ema = sum(prices[max(0,i-19):i+1])/min(i+1,20)
        rsi = random.randint(10,90)
        macd = random.uniform(-0.003,0.003)
        stoch = random.randint(10,90)
        boll_hi = max(prices[max(0,i-19):i+1])

        vote = 'NONE'
        if prices[i]>ema: vote='BUY'; confirmed+=0.2
        else: vote='SELL'; confirmed+=0.2
        if rsi<30: vote='BUY'; confirmed+=0.2
        elif rsi>70: vote='SELL'; confirmed+=0.2
        if macd>0: vote='BUY'; confirmed+=0.2
        else: vote='SELL'; confirmed+=0.2
        if stoch<30: vote='BUY'; confirmed+=0.2
        elif stoch>70: vote='SELL'; confirmed+=0.2
        if prices[i]>boll_hi: vote='BUY'; confirmed+=0.2
        else: vote='SELL'; confirmed+=0.2

        direction_votes.append(vote)
        if vote=='BUY': buy_indices.append(i)
        elif vote=='SELL': sell_indices.append(i)

    direction_votes = [d for d in direction_votes if d!='NONE']
    direction = max(set(direction_votes), key=direction_votes.count)
    confirmed_rounded = round(confirmed)

    send_graph = False
    signal_strength = '❌ Нет подходящего сигнала'

    if only_strong:
        if confirmed_rounded >=4 and signal_type=='Сильный сигнал':
            send_graph = True
            signal_strength = '✅ Сильный сигнал'
        elif confirmed_rounded==7 and signal_type=='VIP сигнал':
            send_graph = True
            signal_strength = '✅ VIP сигнал'
    else:
        if signal_type == 'Все сигналы':
            send_graph = True
            signal_strength = '✅ Сигнал готов'
        elif signal_type == 'Сильный сигнал' and confirmed_rounded >=4:
            send_graph = True
            signal_strength = '✅ Сильный сигнал'
        elif signal_type == 'VIP сигнал' and confirmed_rounded ==7:
            send_graph = True
            signal_strength = '✅ VIP сигнал'

    msg_text = (f"Пара: {pair}\nВремя экспирации: {exp}\nНаправление: {direction}\n"
                f"Подтверждено индикаторов: {confirmed_rounded}/7\nСигнал: {signal_strength}")

    if send_graph:
        bot.send_message(chat_id,msg_text)
        buf = plot_signal(prices, buy_indices, sell_indices)
        bot.send_photo(chat_id, buf)
    else:
        bot.send_message(chat_id,msg_text)

    signal_history.append((datetime.now(),pair,direction,confirmed_rounded))

# ----------------- ИСТОРИЯ -----------------
def show_history(chat_id):
    text = "Последние 10 сигналов:\n"
    for s in signal_history[-10:]:
        text += f"{s[0].strftime('%H:%M')} {s[1]} {s[2]} {s[3]}\n"
    bot.send_message(chat_id,text)

# ----------------- СТАТИСТИКА -----------------
def show_stats(chat_id):
    if not signal_history:
        bot.send_message(chat_id,"Статистика пока пуста")
        return
    df = pd.DataFrame(signal_history,columns=["time","pair","dir","count"])
    stats = df.groupby("pair")["count"].mean()
    msg = "Среднее подтверждение индикаторов по парам:\n"
    for p,v in stats.items():
        msg += f"{p}: {v:.2f}/7\n"
    bot.send_message(chat_id,msg)

# ----------------- ЗАПУСК -----------------
bot.infinity_polling()
