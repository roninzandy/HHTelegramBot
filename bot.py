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
    sti = open('static/sticker.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)
    bot.send_message(message.chat.id, 'Добро пожаловать, {0.first_name}!, \nЯ - <b>{1.first_name}</b>, короче говоря бот.'.format(message.from_user, bot.get_me()),
    parse_mode='html')
    if chat_id not in subscribed_users:
        subscribed_users[chat_id] = True

def send_hh_message():
    while True:
        try:
            data_from_parser = run_parser()
            if data_from_parser:
                for chat_id in subscribed_users:
                    for i in data_from_parser:
                        result = ''
                        for key, value in i.items():
                            if key == 'Title':
#                               result += f'<a href="{i["Link"]}">{value}</a>\n'
                                result += f'<b><a href="{i["Link"]}">{value}</a></b>\n'
                            elif key == 'Salary' or key == 'Company':
                                result += f'<b>{value}</b>\n'
                        bot.send_message(chat_id, result, parse_mode="HTML", disable_web_page_preview=True)

            print(subscribed_users)
            time.sleep(1800)
        except Exception as e:
            print("Ошибка при рассылке:", e)



if __name__ == '__main__':
    exit_event = threading.Event()
    t = threading.Thread(target=send_hh_message)
    t.daemon = True
    t.start()
    bot.polling(none_stop=True)

