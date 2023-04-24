import re
import telebot
import config
import bs4
from bs4 import BeautifulSoup
import requests
import openai
import time

bot = telebot.TeleBot(config.Tg_token)
openai.api_key = config.OpAi_token


def chat_gpt_call(request, _temperature, _max_tokens):
    response1 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are assistant who summarize text."},
                  {"role": "user", "content": request}],
        temperature=_temperature,
        max_tokens=_max_tokens,
        # top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=1
    )
    return response1['choices'][0]['message']['content']


@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Hello, {message.from_user.first_name} {message.from_user.last_name}'
    bot.send_message(message.chat.id, mess, parse_mode='html')
@bot.message_handler()
def get_text(message):
    some_exp = r'^(https?:\/\/)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*$'
    if re.fullmatch(some_exp, message.text):
        response = requests.get(message.text)
        soup = BeautifulSoup(response.text, features='html.parser')
        text_ = soup.get_text().replace('\n', ' ')
        text_spl = text_.split(" ")
        text_spl_clear = list(filter(None, text_spl))
        text_spl_clear1 = list(filter(None, text_spl))
        while len(text_spl_clear) > 2000:
            sum_res = ''
            for i in range(0, len(text_spl_clear), 2000):
                text_chunk_array = text_spl_clear[i:i+2000]
                text_chunk = ' '.join(text_chunk_array)
                result = chat_gpt_call(text_chunk, 0.7, 1000)
                sum_res = sum_res + " " + result
                time.sleep(5)
            result_sum = chat_gpt_call(sum_res, 0.7, 1000)
            if len(result_sum) >= 2000:
                text_spl_clear = result_sum
            else:
                bot.send_message(message.chat.id, result_sum)
                text_spl_clear = result_sum
        if len(text_spl_clear1) < 2000:
            text_str = ' '.join(text_spl_clear1)
            result_2 = chat_gpt_call(text_str, 0.7, 2000)
            bot.send_message(message.chat.id, result_2)
    else:
        bot.send_message(message.chat.id, message.text, parse_mode='html')

bot.polling(none_stop=True, interval=0)

