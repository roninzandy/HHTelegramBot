import threading
import time
import telebot

import config

from main import run_parser

bot = telebot.TeleBot(config.TOKEN)

subscribed_users = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    chat_id = message.chat.id
    #sti = open('static/sticker.webp', 'rb')
    #bot.send_sticker(message.chat.id, sti)
    bot.send_message(message.chat.id, 'Добро пожаловать, {0.first_name}!, \nЯ - <b>{1.first_name}</b>, короче говоря бот.'.format(message.from_user, bot.get_me()),
    parse_mode='html')
    if chat_id not in subscribed_users:
        subscribed_users[chat_id] = True

def send_hh_message():
    while True:
        try:
            data_from_parser = run_parser()
            for chat_id in subscribed_users:
                if isinstance(data_from_parser, str):

                    bot.send_message(chat_id, data_from_parser)
                else:
                    for i in data_from_parser:
                        result = ''
                        for k, v in i.items():
                            result += f'{k}: {v}\n'
                        bot.send_message(chat_id, result)

            print(subscribed_users)
            time.sleep(5)
        except Exception as e:
            print("Ошибка при рассылке:", e)



if __name__ == '__main__':
    exit_event = threading.Event()
    t = threading.Thread(target=send_hh_message)
    t.daemon = True
    t.start()
    bot.polling(none_stop=True)

