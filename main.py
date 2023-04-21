import re
import telebot
import config
import bs4
from bs4 import BeautifulSoup
import requests
import openai

bot = telebot.TeleBot(config.Tg_token)
openai.api_key = config.OpAi_token
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
        text_spl = text_.split()
        sum_res = ''
        for i in range(0, len(text_spl), 700):
            i = text_spl[i:i+700]
            i = ' '.join(i)
            response1 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Ты ассистент, который обобщает текст."},
                     {"role": "user", "content": i}],
            temperature=0.7,
            max_tokens=1550,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=1
            )
            result = response1['choices'][0]['message']['content']
            sum_res = sum_res + result

        sum_res1 = ' '
        response2 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Ты ассистент, который обобщает текст."},
                     {"role": "user", "content": sum_res}],
            temperature=0.7,
            max_tokens=2000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=1
            )
        result2 = response2['choices'][0]['message']['content']
        sum_res1 = sum_res1 + result2

        if len(sum_res1) < 4096:
            bot.send_message(message.chat.id, sum_res1)
        else:
            for j in range(0, len(sum_res1)):
                j = sum_res1[j:j+4090]
                bot.send_message(message.chat.id, j)

    else:
        bot.send_message(message.chat.id, message.text, parse_mode='html')

bot.polling(none_stop=True, interval=0)

