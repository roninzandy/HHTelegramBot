from datetime import datetime
import sqlite3


# def connect(func):
#     def wrapper():
#         connection = sqlite3.connect('database.db')
#         cursor = connection.cursor()
#         func()
#         connection.commit()
#         connection.close()
#     return wrapper

def create_table():
    """
    Функция создания таблицы в БД с данными о вакансиях.
    """


    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    try:
        cursor.execute('CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, "title" TEXT, '
                       '"salary" VARCHAR(255), "company" TEXT, "location" VARCHAR(255), "link" TEXT, "img" TEXT, '
                       '"date" TEXT)')

        connection.commit()
        connection.close()
        print('Изменения внесены в таблицу.')

    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def insert_data(lst_telegram):
    """
    Функция добавления данных о новых вакансиях в БД.
    """

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    for item in lst_telegram:
        title = item['Title']
        salary = item.get('Salary', None)
        company = item.get('Company', None)
        location = item.get('Location', None)
        link = item.get('Link', None)
        img = item.get('Image', None)
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor.execute('''INSERT INTO data ("title", "salary", "company", "location", "link", "img", "date")
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (title, salary, company, location, link, img, date))
        except sqlite3.Error as e:
            print(f"Ошибка при вставке данных: {e}")

    connection.commit()
    connection.close()

    print('Внесение новых данных в БД выполнено.')


def select_data():
    """
    Функция возвращения набора данных из БД.
    """

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM data')
    rows = cursor.fetchall()
    data_list = []
    for row in rows:
        _, title, salary, company, location, link, img, _ = row
        data = {
            'Title': title,
            'Salary': salary,
            'Company': company,
            'Location': location,
            'Link': link,
            'Image': img
        }

        data_list.append(data)

    connection.close()
    return data_list


def create_table_for_telegram_users():
    """
    Функция создания таблицы в БД с данными о подписанных на телеграм-бота пользователей.
    """

    try:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        cursor.execute('CREATE TABLE IF NOT EXISTS telegram_users (id INTEGER PRIMARY KEY, chat_id VARCHAR(255),'
                       ' "date" TEXT, period VARCHAR(255), keyword VARCHAR(255))')

        connection.commit()
        connection.close()

    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def insert_data_for_telegram_users(chat_id, period, keyword):
    """
    Функция добавления данных о новых пользователях телеграм-бота в БД.
    """

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        cursor.execute('''INSERT INTO telegram_users (chat_id, "date", period, keyword) VALUES (?, ?, ?, ?)''',
                       (chat_id, date, period, keyword))
    except sqlite3.Error as e:
        print(f"Ошибка при вставке данных: {e}")

    connection.commit()
    connection.close()

    print('Внесение новых данных о пользователях в БД выполнено.')

def select_chat_id_for_telegram_users():
    """
    Функция возвращения набора данных о пользователях телеграм-бота из БД.
    """

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM telegram_users')
    rows = cursor.fetchall()

    chat_ids = []
    for row in rows:
        chat_ids.append(int(row[1]))

    connection.close()
    return chat_ids

def select_period_for_telegram_users(period):
    """
    Функция возвращения id пользователей телеграм-бота из БД.
    """

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM telegram_users WHERE period = ?', (period,))
    rows = cursor.fetchall()

    chat_ids = []
    for row in rows:
        chat_ids.append(int(row[1]))

    connection.close()
    return chat_ids

def update_period_for_telegram_users(chat_id, period):
    """
    Функция изменения периода рассылки сообщения для пользователя телеграм-бота.
    """

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('UPDATE telegram_users SET period = ? WHERE chat_id = ?', (period, chat_id))

    connection.commit()
    connection.close()

    print('Внесение новых данных о пользователях в БД выполнено.')

def update_keyword_for_telegram_users(chat_id, keyword):
    """
    Функция изменения ключевого слова поиска для пользователя телеграм-бота.
    """

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('UPDATE telegram_users SET keyword = ? WHERE chat_id = ?', (keyword, chat_id))

    connection.commit()
    connection.close()

    print('Внесение новых данных о пользователях в БД выполнено.')


def delete_user(chat_id):
    """
    Функция удаления пользователя
    """
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM telegram_users WHERE chat_id = ?", (chat_id,))
    connection.commit()
    connection.close()

    print('Пользователь удален из БД.')


