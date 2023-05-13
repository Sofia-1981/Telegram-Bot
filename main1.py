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

bot = telebot.TeleBot(config.Tg_token)
openai.api_key = config.OpAi_token


@bot.message_handler(commands=['start']) #знакомимся: фиксируем id, имя, фамилию
def info_about_user(message):
    mess = f'Привет, {message.from_user.first_name} {message.from_user.last_name}'
    bot.send_message(message.chat.id, mess, parse_mode='html')
    global first_name_
    first_name_ = message.from_user.first_name
    global last_name_
    last_name_ = message.from_user.last_name
    global id_
    id_ = message.from_user.id
    bot.send_message(message.chat.id, "Пришли мне твою электронную почту, я внесу тебя в записную книжку", parse_mode='html')
    @bot.message_handler(content_types=['text'])  # получаем электронный адрес пользователя
    def mail_user(message):
        global email_
        email_ = message.text
        def send_test_email(addr_from, addr_to, msg_subj): # отправка тестового письма для проверки корректности адреса
            msg = MIMEMultipart()
            password = config.password
            msg['From'] = addr_from
            msg['To'] = addr_to
            msg['Subject'] = msg_subj
            server = smtplib.SMTP('smtp.gmail.com: 587')
            server.starttls()
            server.login(msg['From'], password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
            server.quit()
        send_test_email('tima56355@gmail.com', email_, "Тестовое письмо")
        markup = types.InlineKeyboardMarkup(row_width=2)
        butt1 = types.InlineKeyboardButton('Письмо получено', callback_data='да')
        butt2 = types.InlineKeyboardButton('Письмо не получено', callback_data='нет')
        markup.add(butt1)
        markup.add(butt2)
        bot.send_message(message.chat.id, "Я отправил тестовое письмо, подтверди его получение", reply_markup=markup)
        @bot.callback_query_handler(func=lambda callback: True)
        def callback_message(callback):
            if callback.data == 'да':
                update_users(id_, first_name_, last_name_, email_) #записали в БД  ID пользователя, имя, фамилию, email
                bot.send_message(message.chat.id, 'Твои данные внесены в мою записную книжку', parse_mode='html')
            else:
                bot.send_message(message.chat.id, 'Проверь правильность указанного эл адреса и направь еще раз', parse_mode='html')

def update_users(id,first_name,last_name,email):
    conn = sqlite3.connect('users.db')  # создаем файл users.db
    global cur
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(userid INT PRIMARY KEY, fname TEXT, lname TEXT,email TEXT);""")
    conn.commit()  # сохраняем изменения
    cur.execute("INSERT or ignore INTO users VALUES(?, ?, ?, ?);", (id,first_name,last_name,email))
    conn.commit()
    sqlite_select_query = """SELECT * from users"""
    cur.execute(sqlite_select_query)
    #cur.execute("DELETE FROM users WHERE lname='Statsenko'")
    records = cur.fetchall() #показать fetchone#fetchmany#fetchall
    print(records)
    #conn.commit()
    conn.close()

# def send_email(addr_from, addr_to, msg_subj):
#     msg = MIMEMultipart()
#     password = config.password
#     msg['From'] = addr_from
#     msg['To'] = addr_to
#     msg['Subject'] = msg_subj
#     fp = open("Calendar.ics")
#     file = MIMEText(fp.read())
#     file.add_header('content-disposition', 'attachment', filename='Calendar.ics')
#     msg.attach(file)
#     server = smtplib.SMTP('smtp.gmail.com: 587')
#     server.starttls()
#     server.login(msg['From'], password)
#     server.sendmail(msg['From'], msg['To'], msg.as_string())
#     server.quit()


# def get_response(request):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "system", "content": "BEGIN:VCALENDAR VERSION:2.0 PRODID:-//ChatGPT//Appointment//EN CALSCALE:GREGORIAN METHOD:REQUEST BEGIN:VTIMEZONE TZID:Asia/Dubai BEGIN:STANDARD DTSTART:19710101T000000 TZOFFSETFROM:+0400 TZOFFSETTO:+0400 END:STANDARD END:VTIMEZONE BEGIN:VEVENT UID:1234567890 ORGANIZER:mailto: ATTENDEE:mailto: DTSTAMP:20220328T000000Z DTSTART;TZID=Asia/Dubai:20230401T000000 DTEND;TZID=Asia/Dubai:20230401T010000 SUMMARY:Appointment with Sergei Karulin LOCATION:Google Meet DESCRIPTION:Please join the Google Meet link to attend the appointment with Sergei Karulin at 12 am UAE time on 1st April 2023. SEQUENCE:0 STATUS:CONFIRMED TRANSP:OPAQUE END:VEVENT END:VCALENDAR"},
#             {"role": "user", "content": request}],
#         temperature=0.7,
#         max_tokens=1500,
#         top_p=1.0,
#         frequency_penalty=0.0,
#         presence_penalty=1
#         )
#     return response['choices'][0]['message']['content']


# @bot.message_handler(content_types=["text"]) #выбираем часть строки для файла .ics
# def messages_ics(message):
#     model_response = get_response(message.text)
#     model_response1 = model_response.split('```')
#     my_file = open("Calendar.ics", "w+")
#     if len(model_response1) == 1:
#         my_file.write(model_response1[0])
#     else:
#         my_file.write(model_response1[1])
#     my_file.close()
#     print(model_response1)
#

#bot.send_document(message.chat.id, open(r'\Users\79298\PycharmProjects\pythonProject7/Calendar.ics', 'rb')) #можно отправить сообщение о проверке почты, пришел ли файл ics



bot.polling(none_stop=True, interval=0)


#bot.register_next_step_handler(message, send_email_test)






