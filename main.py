import re
import telebot
import bs4
from bs4 import BeautifulSoup
import requests

bot = telebot.TeleBot('6201956998:AAE_AAQJiAEVuGHAyGrzyiZ73yw1bmZeoj8')
@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Привет, {message.from_user.first_name} {message.from_user.last_name}'
    bot.send_message(message.chat.id, mess, parse_mode='html')

@bot.message_handler()
def get_text(message):
    some_exp = r'^(https?:\/\/)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*$'
    if re.fullmatch(some_exp, message):
        message=urllib(message)
        response = requests.get(message) # ошибка здесь,message должен поступить как url адрес
        soup = BeautifulSoup(response.text)
        text_ = soup.get_text()
        bot.send_message(message.chat.id, text_, parse_mode='html')
    else:
        bot.send_message(message.chat.id, message.text, parse_mode='html')



bot.polling(none_stop=True, interval=0)
