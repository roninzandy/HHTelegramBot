from datetime import datetime
import os
import random
import re
import sqlite3
from time import sleep
import telebot

import config
import db

from parsing import run_parsing


class MyBot:

    bot = telebot.TeleBot(config.TOKEN_TEST)
    bot_active = True
    admin_users = {}

    MIN_PERIOD = 10 * 60
    MAX_PERIOD = 60 * 60
    ALLOWED_PERIODS = list(range(MIN_PERIOD, MAX_PERIOD + 1, 600))
    time_between_scanning = 20 * 60
    keyword = 'python'

    try:
        db.select_data_for_telegram_users()
    except sqlite3.OperationalError:
        # Если активируется исключение, значит, таблица 'telegram_users' отсутствует и ее нужно создать.
        db.create_table_for_telegram_users()

    @bot.message_handler(commands=['start'])
    def welcome(message):
        if MyBot.bot_active:
            print(message.chat.username)
            chat_id = message.chat.id
            with open('static/hh_preview.png', 'rb') as img_preview:
                AdminPanel.bot.send_photo(chat_id, photo=img_preview)
            MyBot.bot.send_message(message.chat.id, f'Добро пожаловать, {message.from_user.first_name}! \n'
                                                    f'Я - <b>{MyBot.bot.get_me().first_name}</b>, '
                                                    'и я буду присылать Вам новые вакансии'
                                                    ' с hh.kz!\n\n'
                                                    'Сканирование проводится каждые '
                                                    f'<b>{int(AdminPanel.time_between_scanning / 60)}</b> минут по '
                                                    f'ключему слову <b>{AdminPanel.keyword}</b>.\n\n',
                                   parse_mode='HTML')

            if chat_id not in db.select_data_for_telegram_users():
                db.insert_data_for_telegram_users(chat_id)

    @staticmethod
    def run():
        MyBot.bot.polling(none_stop=True)

class AdminPanel(MyBot):
    @MyBot.bot.message_handler(commands=['admin'])
    def admin(message):
        chat_id = message.chat.id
        if chat_id in AdminPanel.admin_users:
            AdminPanel.admin_success(message)
        else:
            AdminPanel.bot.send_message(message.chat.id, 'Введите пароль для входа в админ-панель.')
            AdminPanel.bot.register_next_step_handler(message, AdminPanel.admin_password)

    def admin_password(message):
        if message.text == config.admin_password:
            AdminPanel.admin_success(message)

    def admin_success(message):
        chat_id = message.chat.id

        hello_admin = ''
        if chat_id not in AdminPanel.admin_users:
            AdminPanel.admin_users[chat_id] = True
            hello_admin = f'Добро пожаловать в админ-панель, {message.from_user.first_name}! ' \
                          f'Теперь у Вас больше власти над ботом! \n\n'
        if AdminPanel.bot_active:
            bot_status = 'бот успешно работает'
        else:
            bot_status = 'бот не работает'
        AdminPanel.bot.send_message(message.chat.id, f'{hello_admin} '
                                                     f'В данный момент <b>{bot_status}</b>.\n\n'
                                                     f'Сканирование проводится каждые '
                                                     f'<b>{int(AdminPanel.time_between_scanning/60)}</b> минут по '
                                                     f'ключему слову <b>{AdminPanel.keyword}</b>.\n\n'
                                                     'Доступные команды:\n\n'
                                                     '/keyword - задается ключевое слово для поиска вакансий (слово '
                                                     'может быть только одно, состоять только из строчных букв).\n'
                                                     '/period [число] - задается время между сканированиями по данному '
                                                     'запросу (10, 20, 30, 40, 50 или 60 минут).\n'
                                                     '/users - выводится количество пользователей, установивших бота.\n'
                                                     '/message - отправить всем объявление всем пользователям.\n'
                                                     '/stop - остановить бота.\n'
                                                     '/run - запустить бота.\n'
                                                     '/error - выводит последнюю запись из журнала журнала ошибок.\n'
                                                     '/adminquit - выйти из админ-панели.', parse_mode='HTML')

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

    @MyBot.bot.message_handler(commands=['error'])
    def show_error(message):
        chat_id = message.chat.id
        if chat_id in AdminPanel.admin_users:
            if os.path.exists('logs.txt'):
                with open('logs.txt', encoding='UTF-8') as f:
                    rows = f.readlines()
                    if len(rows) > 0:
                        AdminPanel.bot.send_message(chat_id, f'{rows[-1]}')
                    else:
                        AdminPanel.bot.send_message(chat_id, 'Журнал ошибок пуст.')
            else:
                AdminPanel.bot.send_message(chat_id, 'Журнал ошибок не создан.')

    @classmethod
    def send_error(cls):
        with open('logs.txt', encoding='UTF-8') as f:
            rows = f.readlines()
            for admin_id in cls.admin_users:
                cls.bot.send_message(admin_id, f'❗️ Возникла ошибка.\n\n ️'
                                               f'❗️ {rows[-1]}')

    @MyBot.bot.message_handler(commands=['keyword'])
    def choose_keyword(message):
        chat_id = message.chat.id
        if chat_id in AdminPanel.admin_users:
            AdminPanel.bot.send_message(chat_id, "Выберите ключевое слово для поиска вакансий.")
            AdminPanel.bot.register_next_step_handler(message, AdminPanel.set_keyword)

    def set_keyword(message):
        chat_id = message.chat.id
        if (len(message.text.split()) == 1) and message.text.isalpha():
            AdminPanel.keyword = message.text
            AdminPanel.bot.send_message(chat_id, f'Теперь поиск будет проводиться по ключевому слову '
                                                 f'<b>{message.text}</b>', parse_mode='HTML')
        else:
            AdminPanel.bot.send_message(chat_id, "Данные введены некорректно: ключевое слово должно быть одним словом"
                                                 "и полностью состоять только из букв.")

    @MyBot.bot.message_handler(commands=['doc', 'document'])
    def handle_document(message):
        chat_id = message.chat.id
        if chat_id in AdminPanel.admin_users:
            AdminPanel.bot.send_message(chat_id, "Отправьте файл в формате .txt")
            AdminPanel.bot.register_next_step_handler(message, AdminPanel.darri_keyword)


    def darri_keyword(message):
        chat_id = message.chat.id
        if message.document.mime_type == 'text/plain':
            # Получаем информацию из документа
            file_info = AdminPanel.bot.get_file(message.document.file_id)
            downloaded_file = AdminPanel.bot.download_file(file_info.file_path)
            text = downloaded_file.decode("utf-8")

        if chat_id in AdminPanel.admin_users:
            AdminPanel.bot.send_message(chat_id, "Введите ключевую фразу, которая будет вставлена между абзацами.")
            AdminPanel.bot.register_next_step_handler(message, AdminPanel.darri, text)

    def darri(message, text):
        chat_id = message.chat.id

        lst_all = []
        lst = []
        lst_repeated = []
        limit = 280
        extra = message.text

        website = 'twitter'
        pattern_test = r'bsky.social'
        matches_test = re.findall(pattern_test, text)
        if matches_test:
            website = 'bluesky'

        print(website)

        pattern = r'@(\w+)'
        matches = re.findall(pattern, text)
        print(len(matches))
        for match in matches:
            if website == 'twitter':
                m = f"@{match}"
            elif website == 'bluesky':
                m = f"@{match}.bsky.social"
            else:
                m = f"@{match}"

            if m not in lst_all:
                lst_all.append(m)
                print(m)
            else:
                lst_repeated.append(m)
                print(f'[repeated] ------------------------------> {m}')
        sleep(1)
        #random.shuffle(lst_all)
        lst_all.sort()
        sleep(1)
        print(f'len(lst_all): {len(lst_all)}')
        lst_all_str = ' '.join(lst_all)
        print(f'lst_all_str: {lst_all_str}')
        lst_all_str_len = len(lst_all_str)
        print(lst_all_str_len)
        amount_of_lists = (lst_all_str_len // (limit - len(extra))) + 2
        print(amount_of_lists)

        # creating dict with lists
        lists = {}
        for i in range(amount_of_lists):
            list_name = f"list_{i}"
            lists[list_name] = []

            # filling lists with limit or symbols
        count = 0
        n = 0
        for i in lst_all:
            x = len(str(i)) + 1
            if (count + x) < (limit - len(extra)):
                lists[f'list_{n}'].append(i)
                count += x
            else:
                count = 0
                n += 1

        # forming final list with lists of dict values
        for list_name, list_items in lists.items():
            if lists[list_name]:
                lst.append(list_items)
        # forming final

        with open('to_kjetll.txt', 'w', encoding='utf-8') as f:
           for x1 in lst:
               f.write(f"\n\n{extra}\n")
               for x2 in x1:
                   f.write(f'{x2} ')

        res = ''

        for x1 in lst:
            res += f"\n\n{extra}\n"
            for x2 in x1:
                res += f'{x2} '
        print(res)

        result = f'\nAmount of dicts: {len(lst)}\nNames found: {len(lst_all) + len(lst_repeated)}\n' \
                 f'Users: {len(lst_all)}\nRepeats: {len(lst_repeated)}\n{lst_repeated}\n💋'

        print(result)

        if os.path.exists("to_kjetll.txt") and os.path.getsize("to_kjetll.txt") > 0:
            AdminPanel.bot.send_document(chat_id, open("to_kjetll.txt", "rb"), caption=result)
        else:
            print("Файл 'to_kjetll.txt' пустой или не существует.")


class MessageSender(AdminPanel):
    def send_message(cls):
        """
        Функция для отправки сообщений пользователям.
        """

        while True:
            if cls.bot_active:
                data_from_parser = run_parsing(AdminPanel.keyword)
                if data_from_parser:
                    for i in data_from_parser:
                        result = ''
                        try:
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
                        except telebot.apihelper.ApiTelegramException as e:
                            pass
                print(f'Подписанные пользователи на рассылку: {db.select_data_for_telegram_users()}')
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open('success.txt', 'a', encoding='UTF-8') as f:
                    f.write(f'[{date}]: Сканирование проведено.\n')

                sleep(cls.time_between_scanning)

            else:
                print('Бот не работает. Ожидается повторное подключение через 5 минут.')
                sleep(60 * 5)  # Таймер для следующей попытки продолжить выполнение кода
                               # в случае, если администратор бота активировал '/stop'.
