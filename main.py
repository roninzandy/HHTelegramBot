"""
Программа для парсинга данных о новых вакансиях с сайта hh.kz и рассылки пользователям с помощью telegram-бота.

Данный модуль является основным. Проект состоит из четырех модулей:
1. main.py - содержит функции для отправки сообщений пользователям.
2. config.py - содержит конфиденциальные данные о telegram-боте.
3. parsing.py - содержит функции для парсинга веб-страниц.
4. db.py - содержит функции для создания таблицы, сохранения и чтения данных из БД.

Программа выполняет следующие шаги:
1. Сохранение страниц в виде html-файлов в папку selenium_data.
2. Парсинг сохраненных страниц и сохранения данных о всех найденных вакансиях по данному запросу.
3. Поиск новых вакансий путем сравнения списка вакансий, полученного в результате парсинга, и вакансий, которые уже
присутствуют в БД.
4. Добавление в БД данных о новых вакансиях.
5. Отправка сообщений с новыми вакансиях пользователям помощью telegram-бота.

Для запуска программы выполните данный модуль.

Для активации telegram-бота добавьте его в telegram по имени @beastchargerbot (https://t.me/beastchargerbot).
"""
import os
import threading
import time
import telebot

import config

from parsing import run_parsing

bot = telebot.TeleBot(config.TOKEN)

subscribed_users = {}


@bot.message_handler(commands=['start'])
def welcome(message):
    chat_id = message.chat.id
    sti = open('static/sticker.webp', 'rb')
    bot.send_sticker(message.chat.id, sti)
    bot.send_message(message.chat.id, 'Добро пожаловать, {0.first_name}!, \nЯ - <b>{1.first_name}</b>, '
                                      'и я буду присылать Вам новые вакансии'
                                      ' с hh.kz!'.format(message.from_user, bot.get_me()), parse_mode='html')
    if chat_id not in subscribed_users:
        subscribed_users[chat_id] = True


def send_hh_message():
    """
    Функция для отправки сообщений пользователям.
    """
    while True:
        try:
            time.sleep(5)
            data_from_parser = run_parsing()
            if data_from_parser:
                for chat_id in subscribed_users:
                    for i in data_from_parser:
                        result = ''
                        for key, value in i.items():
                            if key == 'Title':
                                result += f'💼 <b><a href="{i["Link"]}">{value}</a></b>\n'
                            elif key == 'Salary':
                                result += f'💰 <b>{value}</b>\n'
                            elif key == 'Company':
                                result += f'🏙️ <b>{value}</b>\n'
                            elif key == 'Image':
                                img_path = f'static/{i[key]}'
                                if os.path.exists(img_path):
                                    with open(img_path, 'rb') as resized_image_file:
                                        bot.send_photo(chat_id, photo=resized_image_file, caption=result, parse_mode='html') #disable_web_page_preview=True)
                                else:
                                    default_img_path = f'static/hh.png'
                                    if os.path.exists(default_img_path):
                                        with open(default_img_path, 'rb') as resized_image_file:
                                            bot.send_photo(chat_id, photo=resized_image_file, caption=result, parse_mode='html')
                                    else:
                                        bot.send_photo(chat_id, photo=None, caption=result,
                                                       parse_mode='html')


            print(f'Подписанные пользователи на рассылку: {subscribed_users}')

            time.sleep(1800)  # Таймер между рассылками: 30 минут.

        except Exception as e:
            print(f'Ошибка при рассылке: {e}')


def main():
    t = threading.Thread(target=send_hh_message)
    t.daemon = True
    t.start()
    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()

