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

bot = telebot.TeleBot(config.Tg_token)
openai.api_key = config.OpAi_token

def get_response(recuest):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "BEGIN:VCALENDAR VERSION:2.0 PRODID:-//ChatGPT//Appointment//EN CALSCALE:GREGORIAN METHOD:REQUEST BEGIN:VTIMEZONE TZID:Asia/Dubai BEGIN:STANDARD DTSTART:19710101T000000 TZOFFSETFROM:+0400 TZOFFSETTO:+0400 END:STANDARD END:VTIMEZONE BEGIN:VEVENT UID:1234567890 ORGANIZER:mailto: ATTENDEE:mailto: DTSTAMP:20220328T000000Z DTSTART;TZID=Asia/Dubai:20230401T000000 DTEND;TZID=Asia/Dubai:20230401T010000 SUMMARY:Appointment with Sergei Karulin LOCATION:Google Meet DESCRIPTION:Please join the Google Meet link to attend the appointment with Sergei Karulin at 12 am UAE time on 1st April 2023. SEQUENCE:0 STATUS:CONFIRMED TRANSP:OPAQUE END:VEVENT END:VCALENDAR"},
            {"role": "user", "content": recuest}],
        temperature=0.7,
        max_tokens=1500,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=1
        )
    return response['choices'][0]['message']['content']

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    model_response = get_response(message.text)
    model_response1 = model_response.split('```')
    my_file = open("Calendar.ics", "w+")
    if len(model_response1) == 1:
        my_file.write(model_response1[0])
    else:
        my_file.write(model_response1[1])
    my_file.close()
    print(model_response1)
#   достаем эл адрес из строки model_response
    model_response_lst = re.split(':|\n|``` ', model_response)
    print(model_response_lst)
    adress = []
    for i in range(len(model_response_lst)):
      if model_response_lst[i]=='ATTENDEE' and model_response_lst[i+1] == 'mailto':
        adress.append(model_response_lst[i+2])
    print(adress)
    msg = MIMEMultipart()
    password = config.password
    addr_from = 'tima56355@gmail.com'
    addr_to = adress[0]   #'sofiya.statsenko@gmail.com' #'sofia1981-s@mail.ru'
    msg_subj = 'первое письмо'
    msg['From'] = addr_from
    msg['To'] = addr_to
    msg['Subject'] = msg_subj
    fp = open("Calendar.ics")
    file = MIMEText(fp.read())
    file.add_header('content-disposition', 'attachment', filename='Calendar.ics')
    msg.attach(file)
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    bot.send_message(message.chat.id, "Successfully sent email to %s" % (msg['To']))



bot.polling(none_stop=True, interval=0)






