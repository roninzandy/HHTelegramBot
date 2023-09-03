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

Для запуска программа необходимо установить следующие библиотеки:
- pyTelegramBotAPI
- telebot
- BeautifulSoup4
- lxml
- selenium
- requests

Для запуска программы выполните данный модуль.

Для активации telegram-бота добавьте его в telegram по имени @beastchargerbot (https://t.me/beastchargerbot).
"""

import os
import re
import threading
import time
import telebot

import config

from parsing import run_parsing

bot = telebot.TeleBot(config.TOKEN_TEST)

bot_active = True
subscribed_users = {}
admin_users = {}

MIN_PERIOD = 20
MAX_PERIOD = 60
ALLOWED_PERIODS = [i for i in range(MIN_PERIOD, MAX_PERIOD+1, 10)]
time_between_scanning = 30




@bot.message_handler(commands=['start'])
def welcome(message):
    if bot_active:
        chat_id = message.chat.id
        bot.send_message(message.chat.id, f'Добро пожаловать, {message.from_user.first_name}! \n'
                                          f'Я - <b>{bot.get_me().first_name}</b>, '
                                          'и я буду присылать Вам новые вакансии'
                                          ' с hh.kz!', parse_mode='HTML')
        if chat_id not in subscribed_users:
            subscribed_users[chat_id] = True


@bot.message_handler(commands=['admin'])
def admin(message):
    bot.send_message(message.chat.id, 'Введите пароль для входа в админ-панель.')
    if message.text == '/admin':
        bot.register_next_step_handler(message, admin_password)


def admin_password(message):
    if message.text == config.admin_password:
        admin_success(message)


@bot.message_handler(commands=['adminquit'])
def admin_quit(message):
    chat_id = message.chat.id
    if chat_id in admin_users:
        del admin_users[chat_id]
        bot.send_message(message.chat.id, 'Вы вышли из админ-панели и стали обычным юзером!')


@bot.message_handler(commands=['users'])
def users(message):
    chat_id = message.chat.id
    if chat_id in admin_users:
        bot.send_message(message.chat.id, f'Количество пользователей, установивших бота: {len(subscribed_users)}')


@bot.message_handler(commands=['stop'])
def stop_bot(message):
    chat_id = message.chat.id
    if chat_id in admin_users:
        global bot_active
        if not bot_active:
            bot.send_message(chat_id, "Бот уже остановлен.")
        else:
            bot.send_message(chat_id, "Бот временно остановлен.")
            bot_active = False


@bot.message_handler(commands=['run'])
def run_bot(message):
    chat_id = message.chat.id
    if chat_id in admin_users:
        global bot_active
        if bot_active:
            bot.send_message(chat_id, "Бот уже запущен.")
        else:
            bot.send_message(chat_id, "Бот запущен.")
            bot_active = True


@bot.message_handler(commands=['message'])
def message_for_users(message):
    chat_id = message.chat.id
    if chat_id in admin_users:
        bot.send_message(chat_id, "Введите объявление для пользователей.")
        bot.register_next_step_handler(message, sending_message_for_users)


def sending_message_for_users(message):
    for user_id in subscribed_users.keys():
        bot.send_message(user_id, f'❗️ {message.text}')


def admin_success(message):
    chat_id = message.chat.id
    if bot_active:
        bot_status = 'бот успешно работает'
    else:
        bot_status = 'бот не работает'

    bot.send_message(message.chat.id, f'Добро пожаловать в админ-панель, {message.from_user.first_name}. '
                                      f'Теперь у Вас больше власти над ботом! \n\n'
                                      f'В данный момент <b>{bot_status}</b>.\n\n'
                                      f'Сканирование проводится каждые <b>{time_between_scanning}</b> минут.\n\n'
                                      'Доступные команды:\n\n'
                                      '/period [число] - задается время (в минутах) между сканированиями по данному '
                                      'запросу.\n'
                                      '/users - выводится количество пользователей, установивших бота.\n'
                                      '/message - отправить всем объявление всем пользователям.\n'
                                      '/stop - остановить бота.\n'
                                      '/run - запустить бота.\n'
                                      '/adminquit - выйти из админ-панели.',
                     parse_mode='HTML')

    if chat_id not in subscribed_users:
        subscribed_users[chat_id] = True
    if chat_id not in admin_users:
        admin_users[chat_id] = True


@bot.message_handler(commands=['period'])
def new_period(message):
    chat_id = message.chat.id
    if chat_id in admin_users:
        result = re.findall(r'\d+', message.text)
        if len(result) == 1:
            new_time_between_scanning = result[0]
            global ALLOWED_PERIODS
            if new_time_between_scanning in ALLOWED_PERIODS:
                global time_between_scanning
                time_between_scanning = new_time_between_scanning
                bot.send_message(chat_id, f'Теперь сканирование будет проводиться каждые <b>{time_between_scanning}</b>'
                                          f' минут.', parse_mode='HTML')
            else:
                bot.send_message(chat_id, f'Значение должно быть в диапазоне от {MIN_PERIOD} до {MAX_PERIOD} минут.')
        else:
            bot.send_message(chat_id, 'Некорректный ввод команды.')


# def time_between_scanning():
#     return 60*30  # Таймер между рассылками: 30 минут.


def send_hh_message():
    """
    Функция для отправки сообщений пользователям.
    """

    while True:
        if bot_active:
            try:
                time.sleep(5)
                data_from_parser = run_parsing()
                if data_from_parser:
                    for i in data_from_parser:
                        result = ''
                        for chat_id in subscribed_users:
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
                                            bot.send_photo(chat_id, photo=resized_image_file, caption=result,
                                                           parse_mode='html')
                                    else:
                                        default_img_path = f'static/hh.png'
                                        if os.path.exists(default_img_path):
                                            with open(default_img_path, 'rb') as resized_image_file:
                                                bot.send_photo(chat_id, photo=resized_image_file, caption=result,
                                                               parse_mode='html')
                                        else:
                                            bot.send_photo(chat_id, photo=None, caption=result,
                                                           parse_mode='html')

                print(f'Подписанные пользователи на рассылку: {subscribed_users}')

                time.sleep(time_between_scanning)

            except Exception as e:
                print(f'Ошибка при рассылке: {e}')
        else:
            time.sleep(60*5)


def main():
    t = threading.Thread(target=send_hh_message)  # Создание потока.
    t.daemon = True  # Необходимо для принудительного завершения программы.
    t.start()
    bot.polling(none_stop=True)


bot.polling(none_stop=True)
#
# if __name__ == '__main__':
#     main()
