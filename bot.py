import copy
from telebot import types
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

    MIN_PERIOD = 10  #*60
    MAX_PERIOD = 60  #*60
    ALLOWED_PERIODS = list(range(MIN_PERIOD, MAX_PERIOD + 1, 10))  #600
    time_between_scanning = MIN_PERIOD  # Время между сканированиями.
    period = 20 #*60  # Время между рассылками по умолчанию.

    data = [{'per': i, 'data': []} for i in ALLOWED_PERIODS]

    ALLOWED_KEYWORDS = ['python', 'django', 'flask']
    keyword = 'python'  # Ключевое слово по умолчанию.

    try:
        db.select_chat_id_for_telegram_users()
    except sqlite3.OperationalError:
        # Если активируется исключение, значит, таблица 'telegram_users' отсутствует и ее нужно создать.
        db.create_table_for_telegram_users()

    @bot.message_handler(commands=['start'])
    def welcome(message):
        if MyBot.bot_active:
            chat_id = message.chat.id
            with open('static/hh_preview.png', 'rb') as img_preview:
                result = f'Добро пожаловать, {message.from_user.first_name}! \n' \
                         f'Я - <b>{MyBot.bot.get_me().first_name}</b>, ' \
                         f'и я буду присылать Вам новые вакансии' \
                         f' с hh.kz!\n\n'\
                         '📩 Рассылка производится каждые ' \
                         f'<b>{int(AdminPanel.period / 60)}</b> минут по ' \
                         f'ключевому слову <b>"{AdminPanel.keyword}"</b>.\n\n' \
                         '⚙️ Доступные команды:\n\n' \
                         '/keyword - задается ключевое слово для поиска вакансий ("python", "django" или "flask").\n' \
                         '/period [число] - задается время между сканированиями по данному ' \
                         'запросу (10, 20, 30, 40, 50 или 60 минут).\n'


                MyBot.bot.send_photo(chat_id, photo=img_preview, caption=result, parse_mode='html')


            if chat_id not in db.select_chat_id_for_telegram_users():
                db.insert_data_for_telegram_users(chat_id, AdminPanel.period, AdminPanel.keyword)

    @bot.message_handler(commands=['period'])
    def new_period(message):
        chat_id = message.chat.id

        period = re.findall(r'\d+', message.text)
        if len(period) == 1:
            new_period = int(period[0])*60
            if new_period in MyBot.ALLOWED_PERIODS:
                db.update_period_for_telegram_users(chat_id, new_period)
                AdminPanel.bot.send_message(chat_id, f'Теперь результаты будут присылаться каждые '
                                                     f'<b>{int(new_period/60)}</b>'
                                                     f' минут.', parse_mode='HTML')
            else:
                AdminPanel.bot.send_message(chat_id, f'Значение должно быть: 10, 20, 30, 40, 50 или 60 минут')
        else:
            AdminPanel.bot.send_message(chat_id, 'Некорректный ввод команды.')


    @bot.message_handler(commands=['keyword'])
    def choose_keyword(message):
        chat_id = message.chat.id

        AdminPanel.bot.send_message(chat_id, "Выберите ключевое слово для поиска вакансий.")
        # if message.text.lower() in MyBot.ALLOWED_KEYWORDS:
        #     AdminPanel.bot.register_next_step_handler(message, AdminPanel.set_keyword)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        # Создаем кнопки 1 и 2
        button1 = types.KeyboardButton("python")
        button2 = types.KeyboardButton("django")
        button3 = types.KeyboardButton("flask")

        # Добавляем кнопки к клавиатуре
        markup.add(button1, button2, button3)

        # Отправляем сообщение с клавиатурой
        AdminPanel.bot.send_message(chat_id, "Выберите ключевое слово для поиска вакансий:", reply_markup=markup)

    def set_keyword(message):
        chat_id = message.chat.id
        #if (len(message.text.split()) == 1) and message.text.isalpha():
        if message.text.lower() in MyBot.ALLOWED_KEYWORDS:
            db.update_keyword_for_telegram_users(chat_id, message.text.lower())
            AdminPanel.bot.send_message(chat_id, f'Теперь поиск будет проводиться по ключевому слову '
                                                 f'<b>{message.text.lower()}</b>', parse_mode='HTML')
        else:
            AdminPanel.bot.send_message(chat_id, "Данные введены некорректно: ключевое слово должно быть одним словом"
                                                 "и полностью состоять только из букв.")

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
                                                         f'{len(db.select_chat_id_for_telegram_users())}')

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
        for user_id in db.select_chat_id_for_telegram_users():
            AdminPanel.bot.send_message(user_id, f'❗️ {message.text}')



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
        owner = '@kjetll_art'
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
        lst_all.remove(owner)
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
        n = 0 #номер словаря
        for i in lst_all:
            x = len(str(i)) + 1  #длина одного имени
            if (count + x) < (limit - len(extra)):
                count += x
            else:
                n += 1
                count = x
            lists[f'list_{n}'].append(i)


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
        period = 0  # Начало временного отсчета
        while True:
            if cls.bot_active:
                period += 10

                if period > 60:
                    period = period % 60

                available_periods = []  # Периоды (кратные текущему периоду). Пользователи с этими периодами после
                                        # текущего сканирования получат рассылку.

                for allowed_period in MyBot.ALLOWED_PERIODS:
                    if period % allowed_period == 0:
                        available_periods.append(allowed_period)



                print(f'Period: {period}')
                print(f'Users" periods for response: {available_periods}')

                for v in MyBot.ALLOWED_KEYWORDS:  # Сканирование для каждого ключевого слова.

                    data_from_parser = run_parsing(v)
                    z_lst = []  # Список буферных данных для отправки пользователям, которые отфитрованы по периодам.
                    for data in MyBot.data:
                        data['data'] += data_from_parser  # Расширение буферных данных с каждым сканированием, пока пользователь не получит рассылку.
                        if data['per'] in available_periods: # В случае совпадения текущего периода и периода пользователя, происходит отправка рассылки и очистка буфера.
                            z_lst.append(copy.deepcopy(data))
                            data['data'].clear()

                    print(f'z_lst: {z_lst}')

                    for datas in z_lst:
                        if datas['data']:
                            for i in datas['data']:
                                for chat_id in db.select_keyword_and_period_for_telegram_users(v, (datas['per'] * 60) % 3600):
                                    result = ''
                                    try:
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
                                    except telebot.apihelper.ApiTelegramException:
                                        db.delete_user(chat_id)

                print(f'Подписанные пользователи на рассылку: {db.select_chat_id_for_telegram_users()}')
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open('success.txt', 'a', encoding='UTF-8') as f:
                    f.write(f'[{date}]: Сканирование проведено.\n')

                sleep(cls.time_between_scanning)  #Пауза между сканированиями

            else:
                print('Бот отключен. Ожидается повторная попытка сканирования через 5 минут.')
                sleep(60 * 5)  # Таймер для следующей попытки продолжить выполнение кода
                               # в случае, если администратор бота активировал '/stop'.
