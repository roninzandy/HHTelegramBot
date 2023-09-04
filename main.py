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
from time import sleep
import telebot

import config
import db

from parsing import run_parsing


class MyBot:

    bot = telebot.TeleBot(config.TOKEN_TEST)
    bot_active = True
    admin_users = {}

    MIN_PERIOD = 10*60
    MAX_PERIOD = 60*60
    ALLOWED_PERIODS = list(range(MIN_PERIOD, MAX_PERIOD + 1, 600))
    print(ALLOWED_PERIODS)
    time_between_scanning = 30*60


    try:
        db.select_data_for_telegram_users()
    except Exception:
        db.create_table_for_telegram_users()




    @bot.message_handler(commands=['start'])
    def welcome(message):
        if MyBot.bot_active:
            chat_id = message.chat.id
            MyBot.bot.send_message(message.chat.id, f'Добро пожаловать, {message.from_user.first_name}! \n'
                                                    f'Я - <b>{MyBot.bot.get_me().first_name}</b>, '
                                                    'и я буду присылать Вам новые вакансии'
                                                    ' с hh.kz!', parse_mode='HTML')

            if chat_id not in db.select_data_for_telegram_users():
                db.insert_data_for_telegram_users(chat_id)

    @staticmethod
    def run():
        MyBot.bot.polling(none_stop=True)



class AdminPanel(MyBot):
    @MyBot.bot.message_handler(commands=['admin'])
    def admin(message):
        AdminPanel.bot.send_message(message.chat.id, 'Введите пароль для входа в админ-панель.')
        if message.text == '/admin':
            AdminPanel.bot.register_next_step_handler(message, AdminPanel.admin_password)

    def admin_password(message):
        if message.text == config.admin_password:
            AdminPanel.admin_success(message)

    def admin_success(message):
        chat_id = message.chat.id
        if AdminPanel.bot_active:
            bot_status = 'бот успешно работает'
        else:
            bot_status = 'бот не работает'

        AdminPanel.bot.send_message(message.chat.id, f'Добро пожаловать в админ-панель, {message.from_user.first_name}. '
                                          f'Теперь у Вас больше власти над ботом! \n\n'
                                          f'В данный момент <b>{bot_status}</b>.\n\n'
                                          f'Сканирование проводится каждые <b>{int(AdminPanel.time_between_scanning/60)}</b> минут.\n\n'
                                          'Доступные команды:\n\n'
                                          '/period [число] - задается время между сканированиями по данному '
                                          'запросу (10, 20, 30, 40, 50 или 60 минут).\n'
                                          '/users - выводится количество пользователей, установивших бота.\n'
                                          '/message - отправить всем объявление всем пользователям.\n'
                                          '/stop - остановить бота.\n'
                                          '/run - запустить бота.\n'
                                          '/adminquit - выйти из админ-панели.',
                                    parse_mode='HTML')

        if chat_id not in AdminPanel.admin_users:
            AdminPanel.admin_users[chat_id] = True

    @MyBot.bot.message_handler(commands=['adminquit'])
    def admin_quit(message):
        chat_id = message.chat.id
        if chat_id in AdminPanel.admin_users:
            del AdminPanel.admin_users[chat_id]
            AdminPanel.bot.send_message(message.chat.id, 'Вы вышли из админ-панели и стали обычным юзером!')

    @MyBot.bot.message_handler(commands=['users'])
    def users(message):
        chat_id = message.chat.id
        if chat_id in AdminPanel.admin_users:
            AdminPanel.bot.send_message(message.chat.id, f'Количество пользователей, установивших бота: '
                                                         f'{len(db.select_data_for_telegram_users())}')

    @MyBot.bot.message_handler(commands=['stop'])
    def stop_bot(message):
        chat_id = message.chat.id
        if chat_id in AdminPanel.admin_users:
            if not AdminPanel.bot_active:
                AdminPanel.bot.send_message(chat_id, "Бот уже остановлен.")
            else:
                AdminPanel.bot.send_message(chat_id, "Бот временно остановлен.")
                AdminPanel.bot_active = False

    @MyBot.bot.message_handler(commands=['run'])
    def run_bot(message):
        chat_id = message.chat.id
        if chat_id in AdminPanel.admin_users:
            if AdminPanel.bot_active:
                AdminPanel.bot.send_message(chat_id, "Бот уже запущен.")
            else:
                AdminPanel.bot.send_message(chat_id, "Бот запущен.")
                AdminPanel.bot_active = True

    @MyBot.bot.message_handler(commands=['message'])
    def message_for_users(message):
        chat_id = message.chat.id
        if chat_id in AdminPanel.admin_users:
            AdminPanel.bot.send_message(chat_id, "Введите объявление для пользователей.")
            AdminPanel.bot.register_next_step_handler(message, AdminPanel.sending_message_for_users)

    def sending_message_for_users(message):
        for user_id in db.select_data_for_telegram_users():
            AdminPanel.bot.send_message(user_id, f'❗️ {message.text}')



    @MyBot.bot.message_handler(commands=['period'])
    def new_period(message):
        chat_id = message.chat.id
        if chat_id in AdminPanel.admin_users:
            result = re.findall(r'\d+', message.text)
            if len(result) == 1:
                new_time_between_scanning = int(result[0])*60
                if new_time_between_scanning in MyBot.ALLOWED_PERIODS:
                    AdminPanel.time_between_scanning = new_time_between_scanning
                    AdminPanel.bot.send_message(chat_id, f'Теперь сканирование будет проводиться каждые '
                                                         f'<b>{int(AdminPanel.time_between_scanning/60)}</b>'
                                                         f' минут.', parse_mode='HTML')
                else:
                    AdminPanel.bot.send_message(chat_id, f'Значение должно быть: 10, 20, 30, 40, 50 или 60 минут')
            else:
                AdminPanel.bot.send_message(chat_id, 'Некорректный ввод команды.')


class MessageSender(AdminPanel):
    def send_message(cls):
        """
        Функция для отправки сообщений пользователям.
        """

        while True:
            if cls.bot_active:
                try:
                    sleep(5)
                    data_from_parser = run_parsing()
                    if data_from_parser:
                        for i in data_from_parser:
                            result = ''
                            for chat_id in db.select_data_for_telegram_users():
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
                                            with open(img_path, 'rb') as image_file:
                                                cls.bot.send_photo(chat_id, photo=image_file, caption=result,
                                                                   parse_mode='html')
                                        else:
                                            default_img_path = f'static/hh.png'
                                            if os.path.exists(default_img_path):
                                                with open(default_img_path, 'rb') as default_image_file:
                                                    cls.bot.send_photo(chat_id, photo=default_image_file,
                                                                       caption=result, parse_mode='html')
                                            else:
                                                cls.bot.send_photo(chat_id, photo=None, caption=result,
                                                                   parse_mode='html')

                    print(f'Подписанные пользователи на рассылку: {db.select_data_for_telegram_users()}')

                    sleep(cls.time_between_scanning)

                except Exception as e:
                    print(f'Ошибка при рассылке: {e}')
            else:
                sleep(60 * 5)




def main():
    my_bot = MessageSender()
    t = threading.Thread(target=my_bot.send_message)  # Создание потока.
    t.daemon = True  # Необходимо для принудительного завершения программы.
    t.start()
    AdminPanel().run()




if __name__ == '__main__':
    main()


