"""Weather. Currency. News.
    Погода. Валюта. Новости.
        WCN_Ru_bot"""

import time
import datetime
from datetime import timedelta
import requests
from pyowm import OWM
from pyowm.utils.config import get_default_config
from newsapi import NewsApiClient
from operator import itemgetter
import telebot
from telebot import types
from geopy.geocoders import Nominatim

owm_key = ''
news_key = ''


def weather(observation):
    """Узнав место, узнаем погоду"""
    try:
        icons = ['🌙', '☀', '⛅', '☁', '🌧', '⛈', '🌨']
        # Погода
        w = observation.weather
        t = w.temperature('celsius')['temp']
        wind = w.wind('meters_sec')['speed']
        # Восход, Закат (по Гринвичу)
        sr1 = w.sunrise_time(timeformat="date")
        sr2 = sr1.strftime("%d.%m.%Y, %H:%M")
        ss1 = w.sunset_time(timeformat="date")
        ss2 = ss1.strftime("%d.%m.%Y, %H:%M")
        # Значки для погоды
        status = w.detailed_status
        status_str = str(status).lower()
        if 'ясно' in status_str or 'солн' in status_str:
            if time.strftime("%d.%m.%Y, %H:%M", time.gmtime()) > sr2:
                if time.strftime("%d.%m.%Y, %H:%M", time.gmtime()) < ss2:
                    icon = icons[1]
                else:
                    icon = icons[0]
            else:
                icon = icons[0]
        elif 'перем' in status_str or 'обл' in status_str or 'прояснен' in status_str:
            if time.strftime("%d.%m.%Y, %H:%M", time.gmtime()) > sr2:
                if time.strftime("%d.%m.%Y, %H:%M", time.gmtime()) < ss2:
                    icon = icons[3] + ' ' + icons[1]
                else:
                    icon = icons[3] + ' ' + icons[0]
            else:
                icon = icons[3] + ' ' + icons[0]
        elif 'пасмурн' in status_str or 'туман' in status_str or 'мгла' in status_str:
            icon = icons[3]
        elif 'дожд' in status_str or 'осадк' in status_str or 'лив' in status_str:
            icon = icons[4]
        elif 'гроз' in status_str or 'гром' in status_str or 'шторм' in status_str:
            icon = icons[5]
        elif 'сне' in status_str or 'бур' in status_str or 'метел' in status_str:
            icon = icons[6]
        else:
            icon = ''
        # Результат по погоде
        info_weather = (status.capitalize() + '  ' + icon + '   ' + str(round(t)) + '°' + '\n\n')
        return str(info_weather + f'Ветер  {wind} м/с\n')
    except:
        pass


def weather_coord(x, y):
    """Определение локации по координатам"""
    global owm_key
    try:
        config_dict = get_default_config()
        config_dict['language'] = 'ru'
        owm = OWM(owm_key, config_dict)
        mgr = owm.weather_manager()
        observation = mgr.weather_at_coords(lat=x, lon=y)
        return weather(observation)
    except:
        pass


def weather_loc(loc):
    """Определение локации по названию"""
    global owm_key
    try:
        config_dict = get_default_config()
        config_dict['language'] = 'ru'
        owm = OWM(owm_key, config_dict)
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(loc)
        return str(loc) + '\n\n' + weather(observation)
    except:
        return str('Запрос не распознан')


def currency():
    """Курсы валют"""
    try:
        data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
        usd_sale = data['Valute']['USD']['Value']
        usd_buy = data['Valute']['USD']['Previous']
        usd = round((usd_sale + usd_buy) / 2, 2)
        eur_sale = data['Valute']['EUR']['Value']
        eur_buy = data['Valute']['EUR']['Previous']
        eur = round((eur_sale + eur_buy) / 2, 2)
        return str(f'Курс $:   {usd} руб.\nКурс €:   {eur} руб.')
    except:
        pass


def top_news():
    """Главные новости на сегодня"""
    global news_key
    try:
        newsapi = NewsApiClient(api_key=news_key)
        headlines = newsapi.get_top_headlines(sources='rbc', language='ru')
        top_headlines_1 = dict(headlines)
        top_headlines_2 = dict(top_headlines_1)['articles']
        headline = itemgetter('title')
        url = itemgetter('url')
        top_headlines_3 = [(headline(item), url(item)) for item in top_headlines_2][:7]
        top_headlines_4 = ''
        for i in top_headlines_3:
            for item in i:
                if 'http' in item:
                    top_headlines_4 += (str(item) + '\n\n')
                else:
                    top_headlines_4 += ('• ' + str(item) + '\n')
        return str(top_headlines_4)
    except:
        pass


def funny_news():
    """Hi-Tech новости"""
    global news_key
    try:
        newsapi = NewsApiClient(api_key=news_key)
        offset = datetime.timezone(datetime.timedelta(hours=3))
        dtn = datetime.datetime.now(offset).strftime("%Y-%m-%d")
        dt_prev = (datetime.datetime.now(offset) - timedelta(days=1)).strftime("%Y-%m-%d")
        headlines = newsapi.get_everything(domains='mail.ru', language='ru', sort_by='relevancy',
                                           from_param=dt_prev, to=dtn)
        top_headlines_1 = dict(headlines)
        top_headlines_2 = dict(top_headlines_1)['articles']
        headline = itemgetter('title')
        url = itemgetter('url')
        top_headlines_3 = [(headline(item), url(item)) for item in top_headlines_2][:7]
        top_headlines_4 = ''
        for i in top_headlines_3:
            for item in i:
                if 'http' in item:
                    top_headlines_4 += (str(item) + '\n\n')
                else:
                    top_headlines_4 += ('• ' + str(item) + '\n')
        return str(top_headlines_4)
    except:
        pass


TOKEN = ''
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    """Кнопки и приветствие бота"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Погода 🌤', request_location=True)
    button2 = types.KeyboardButton('Валюта 💵')
    button3 = types.KeyboardButton('Новости 📰')
    button4 = types.KeyboardButton('Интересное 🎮')
    markup.add(button1, button2, button3, button4)
    stick = open('sticker_johny.webp', 'rb')
    bot.send_sticker(message.chat.id, stick)
    bot.send_message(message.chat.id, "Привет, {0.first_name}! Посмотрим, что там в мире."
                     .format(message.from_user, bot.get_me()), parse_mode='html')
    bot.send_message(message.chat.id, "-------------------------------------------",
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['help'])
def info(message):
    """Справка"""
    help_text = ('Привет!\nЯ бот, который поможет тебе узнать погоду и новости.\n\n'
                 'Чтобы узнать погоду в текущем месте, курсы валют или новости - нажми на '
                 'соответствующую кнопку на клавиатуре внизу.\nТакже ты можешь ввести свой запрос вручную.\n\n'
                 'Чтобы узнать погоду в другом городе или регионе - просто введи его название.')
    bot.send_message(message.chat.id, help_text, parse_mode='html')


@bot.message_handler(content_types=['text'])
def dialog(message):
    """Ответы бота"""
    try:
        bad_words = ("жоп", "пизд", "хуй", "наху", "хуя", "хую", "хуе", "хуё", "дур", "хер", " бля", "идиот", "суч",
                     " еба", "еби", "ёб", "боеб", "поеба", "заеба", "доеба", "наеба", "выеба",
                     " сук", "говн", "шлюх", "падл", "пидр", "пидо", "пида", "залуп", "муд", "урод",
                     "fck", "fuck", "whore", "bitch", "btch", "idiot", "fool")
        johny_fk = open('johny_fk_u.webp', 'rb')
        if message.chat.type == 'private':
            def bad():
                """Определение матюков"""
                for i in bad_words:
                    if i in message.text.lower():
                        return True
                    else:
                        pass
            if message.text == 'Погод' or 'погода' in str(message.text).lower():
                bot.send_message(message.chat.id, 'Используй кнопку или введи название города или региона')
            elif message.text == 'Валюта 💵' or 'валют' in str(message.text).lower() \
                    or 'курс' in str(message.text).lower() or 'евро' in str(message.text).lower() \
                    or 'доллар' in str(message.text).lower():
                bot.send_message(message.chat.id, currency())
            elif message.text == 'Новости 📰' or 'новост' in str(message.text).lower():
                bot.send_message(message.chat.id, top_news(), disable_web_page_preview=True)
            elif message.text == 'Интересное 🎮' or 'интересное' in str(message.text).lower() \
                    or 'развлечения' in str(message.text).lower() or 'фан' in str(message.text).lower():
                bot.send_message(message.chat.id, funny_news(), disable_web_page_preview=True)
            elif bad():
                bot.send_sticker(message.chat.id, johny_fk)
            else:
                bot.send_message(message.chat.id, weather_loc(message.text))
    except:
        pass


@bot.message_handler(content_types=["location"])
def location(message):
    """Ответ на сообщение Погода (текущая локация)"""
    try:
        if message.location is not None:
            place = (Nominatim(user_agent="name_of_your_app")
                     .reverse('{} {}'.format(message.location.latitude, message.location.longitude)))
            place_state = str(place.raw['address']['state']) + ', ' + str(place.raw['address']['county'] + '\n\n')
            x = float("%s" % message.location.latitude)
            y = float("%s" % message.location.longitude)
            bot.send_message(message.chat.id, place_state + weather_coord(x, y))
        else:
            bot.send_message(message.chat.id, 'Локация не определена')
    except:
        pass


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except:
        pass
