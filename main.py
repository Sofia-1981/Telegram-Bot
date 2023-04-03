import telebot

bot = telebot.TeleBot('')
@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Привет, {message.from_user.first_name} {message.from_user.last_name}'
    bot.send_message(message.chat.id, mess, parse_mode='html')

@bot.message_handler()
def get_text(message):
    bot.send_message(message.chat.id, message.text, parse_mode='html')


bot.polling(none_stop=True)


