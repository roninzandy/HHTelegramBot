from datetime import datetime
import sqlite3

def create_table(lst_json):
    """
    Функция создания таблицы в БД.
    """

    try:
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        cursor.execute('CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, "title" TEXT, '
                       '"salary" VARCHAR(255), "company" TEXT, "location" VARCHAR(255), "link" TEXT, "date" TEXT)')

        for item in lst_json:
            title = item['Title']
            salary = item.get('Salary', None)
            company = item.get('Company', None)
            location = item.get('Location', None)
            link = item.get('Link', None)
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                cursor.execute('''INSERT INTO data ("title", "salary", "company", "location", "link", "date")
                                VALUES (?, ?, ?, ?, ?, ?)''',
                               (title, salary, company, location, link, date))
            except sqlite3.Error as e:
                print(f"Ошибка при вставке данных: {e}")
        connection.commit()
        connection.close()
        print('Изменения внесены в таблицу')

    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")



def insert_data(lst_telegram):
    """
    Функция добавления новых данных в БД.
    """

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    for item in lst_telegram:
        title = item['Title']
        salary = item.get('Salary', None)
        company = item.get('Company', None)
        location = item.get('Location', None)
        link = item.get('Link', None)
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor.execute('''INSERT INTO data ("title", "salary", "company", "location", "link", "date")
                            VALUES (?, ?, ?, ?, ?, ?)''',
                           (title, salary, company, location, link, date))
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
        id, title, salary, company, location, link, date = row
        data = {
            'Title': title,
            'Salary': salary,
            'Company': company,
            'Location': location,
            'Link': link
        }

        data_list.append(data)

    connection.close()
    return data_list



