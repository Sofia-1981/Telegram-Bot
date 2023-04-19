import re
import telebot
import bs4
from bs4 import BeautifulSoup
import requests
import openai

bot = telebot.TeleBot('6201956998:AAE_AAQJiAEVuGHAyGrzyiZ73yw1bmZeoj8')
openai.api_key = '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'
@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Привет, {message.from_user.first_name} {message.from_user.last_name}'
    bot.send_message(message.chat.id, mess, parse_mode='html')

@bot.message_handler()
def get_text(message):
    some_exp = r'^(https?:\/\/)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*$'
    if re.fullmatch(some_exp, message.text):
        response = requests.get(message.text)
        soup = BeautifulSoup(response.text, features='html.parser')
        text_ = soup.get_text()
        response1 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Ты ассистент, который обобщает текст."},
                  {"role": "user", "content": text_}],
        temperature=0.7,
        max_tokens=600,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=1
        )
        bot.send_message(message.chat.id, response1['choices'][0]['message']['content'])
    else:
        bot.send_message(message.chat.id, message.text, parse_mode='html')

bot.polling(none_stop=True, interval=0)
