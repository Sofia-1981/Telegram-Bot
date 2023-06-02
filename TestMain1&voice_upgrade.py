import re
import telebot
import config
import bs4
from bs4 import BeautifulSoup
import requests
import openai
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from telebot import types
import random
import soundfile as sf


bot = telebot.TeleBot(config.Tg_token)
openai.api_key = config.OpAi_token

bot = telebot.TeleBot(config.Tg_token)
openai.api_key = config.OpAi_token
rate_limit_min = 3
delay = 69/rate_limit_min

# инструкция help:
@bot.message_handler(commands=['help'])
def info_about_bot(message):
    bot.send_message(message.chat.id,"Я умею: 1. Обобщать тексты, для этого пришли мне ссылку в чат; 2. Формировать файл ics для создания встречи в календаре. Для этого начни свое сообщение с: Please generate an appointment (я также приму голосовое сообщение от тебя)", parse_mode='html')
# регистрация пользователя
@bot.message_handler(commands=['start'])
def info_about_user(message):
    mess = f'Привет, {message.from_user.first_name} {message.from_user.last_name}'
    bot.send_message(message.chat.id, mess, parse_mode='html')
    first_name_ = message.from_user.first_name
    last_name_ = message.from_user.last_name
    id_ = message.from_user.id
    conn = sqlite3.connect('users.db')  # создаем файл users.db
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(userid INT PRIMARY KEY, fname TEXT, lname TEXT, email TEXT, code INTEGER, registrated boolean)""")
    cur.execute('''SELECT*FROM users WHERE userid =?''', (int(id_), ))
    conn.commit()
    if len(cur.fetchall()) == 0:
        email_ = '0'
        code_ = 0
        registrated_ = 0
        #cur.execute("DELETE FROM users WHERE lname='Statsenko'")
        cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", (id_, first_name_, last_name_, email_, 0, registrated_))
        cur.execute("""SELECT * from users""")
        conn.commit()
        a = int("".join(random.sample("123456789", 4)))
        print(a)
        cur.execute('''UPDATE users SET code=? WHERE userid=?''', (a, id_))
        conn.commit()
        cur.close()
        bot.send_message(message.chat.id, "Пришли мне твою электронную почту", parse_mode='html')
        bot.register_next_step_handler(message, email, a, id_)
    else:
        pass
def email(message,a, id_):
    email_from_user = message.text
    send_mail_user(email_from_user, "Подтверждение эл почты", str(a), 'no')
    bot.send_message(message.chat.id, "Я отправил тебе 4-х значный код на указанный адрес, пришли его в чат", parse_mode='html')
    bot.register_next_step_handler(message, appr_cod, a, id_, email_from_user)
def appr_cod(message, a, id_, email_from_user):
    if a == int(message.text):
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('''UPDATE users SET email=?, registrated =? WHERE userid=?''', (email_from_user, 1, id_))
        conn.commit()
        bot.send_message(message.chat.id, "Регистрация завершена, теперь отправь в чат /help, что бы узнать как работает бот", parse_mode='html')
        cur.execute('''SELECT*FROM users''')
        conn.commit()
        for i in cur.fetchall():
            print(i)
        cur.close()

## обобщение текста:
def chat_gpt_call(request, _temperature, _max_tokens):
    response1 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are assistant who summarize text."},
                  {"role": "user", "content": request}],
        temperature=_temperature,
        max_tokens=_max_tokens,
        # top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=1)
    return response1['choices'][0]['message']['content']

@bot.message_handler(regexp=r'^(https?:\/\/)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*$')
def get_text(message):
    some_exp = r'^(https?:\/\/)?([\w-]{1,32}\.[\w-]{1,32})[^\s@]*$'
    if re.fullmatch(some_exp, message.text):
        response = requests.get(message.text)
        soup = BeautifulSoup(response.text, features='html.parser')
        text_ = soup.get_text().replace('\n', ' ')
        text_spl = text_.split(" ")
        text_spl_clear = list(filter(None, text_spl))
        try:
            a = True
            while a:
                a = False
                sum_res = ''
                for i in range(0, len(text_spl_clear), 2000):
                    text_chunk_array = text_spl_clear[i:i + 2000]
                    text_chunk = ' '.join(text_chunk_array)
                    time_request = []
                    result = chat_gpt_call(text_chunk, 0.7, 1000)
                    t = datetime.now()
                    time_request.append(t)
                    sum_res = sum_res + " " + result
                    t1 = datetime.now()
                    dif1 = t1 - time_request[0]
                    if dif1.seconds < delay:
                        time.sleep(delay - dif1.seconds)
                result_sum = chat_gpt_call(sum_res, 0.7, 1000)
                if len(result_sum) >= 2000:
                    text_spl_clear = list(result_sum)
                else:
                    bot.send_message(message.chat.id, result_sum)
        except:
                markup = types.InlineKeyboardMarkup()
                butt = types.InlineKeyboardButton('Try again in 20 sec', callback_data='send')
                markup.add(butt)
                bot.send_message(message.chat.id, 'Unsuccessful attempt', reply_markup=markup)

                @bot.callback_query_handler(func=lambda callback: True)
                def callback_message(callback):
                    if callback.data == 'send':
                        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                              text='Expect...')
                        get_text(message)
                pass
    else:
        pass

## календарь: формирование файла ics, принимаем тест и голос
def get_response(req):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system",
                   "content": "BEGIN:VCALENDAR VERSION:2.0 PRODID:-//ChatGPT//Appointment//EN CALSCALE:GREGORIAN METHOD:REQUEST BEGIN:VTIMEZONE TZID:Asia/Dubai BEGIN:STANDARD DTSTART:19710101T000000 TZOFFSETFROM:+0400 TZOFFSETTO:+0400 END:STANDARD END:VTIMEZONE BEGIN:VEVENT UID:1234567890 ORGANIZER:mailto: ATTENDEE:mailto: DTSTAMP:20220328T000000Z DTSTART;TZID=Asia/Dubai:20230401T000000 DTEND;TZID=Asia/Dubai:20230401T010000 SUMMARY:Appointment with Sergei Karulin LOCATION:Google Meet DESCRIPTION:Please join the Google Meet link to attend the appointment with Sergei Karulin at 12 am UAE time on 1st April 2023. SEQUENCE:0 STATUS:CONFIRMED TRANSP:OPAQUE END:VEVENT END:VCALENDAR"},
                  {"role": "user", "content": req}],
        temperature=0.7,
        max_tokens=1500,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=1)
    return response['choices'][0]['message']['content']

def send_mail_user(email_str, subj_str, body, file):
    msg = MIMEMultipart()
    password = config.password
    msg['From'] = 'tima56355@gmail.com'
    addr_to = email_str
    msg['To'] = addr_to
    msg['Subject'] = subj_str
    body = MIMEText(body)
    msg.attach(body)
    if file == 'yes':
        fp = open("Calendar.ics")
        file = MIMEText(fp.read())
        file.add_header('content-disposition', 'attachment', filename='Calendar.ics')
        msg.attach(file)
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
    elif file == 'no':
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
    return print('Письмо отправлено')

@bot.message_handler(content_types=['text','voice'])
def start_filter(message):
    if message.text and message.text.startswith('Please generate an appointment '):
        message1 = message.text
        print(type(message1))
        bot.send_message(message.chat.id, 'Отправляю письмо с файлом .ics тебе в почту')
        model_response = get_response(message1)
        #print(model_response)
        model_response1 = model_response.split('```')
        my_file = open("Calendar.ics", "w+")
        if len(model_response1) == 1:
            my_file.write(model_response1[0])
        else:
            my_file.write(model_response1[1])
        my_file.close()
    elif message.voice:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('user_voice.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)
        data, samplerate = sf.read('user_voice.ogg')
        sf.write('user_voice.mp3', data, samplerate)
        audio_file = open("user_voice.mp3", "rb")
        transcript = openai.Audio.translate("whisper-1", audio_file)
        print(transcript['text'])
        info_for_ics = get_response(transcript['text'])
        print(info_for_ics)
        model_response1 = info_for_ics.split('```')
        my_file = open("Calendar.ics", "w+")
        if len(model_response1) == 1:
            my_file.write(model_response1[0])
        else:
            my_file.write(model_response1[1])
        my_file.close()
        bot.send_message(message.chat.id, 'Отправляю письмо с файлом .ics тебе в почту')
    else:
        bot.send_message(message.chat.id, 'Я не знаю такой команды', parse_mode='html')
    conn = sqlite3.connect('users.db')
    id = message.from_user.id
    cur = conn.cursor()
    cur.execute('''SELECT email FROM users WHERE userid=?''', (int(id),))
    email_turp = cur.fetchone()
    email_str = ''.join(email_turp)
    conn.commit()
    conn.close()
    send_mail_user(email_str, 'Новая встреча', 'Прилагаю файл ics', 'yes')





bot.polling(none_stop=True, interval=0)



