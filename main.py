"""
Программа создана для парсинга данных о новых вакансиях с сайта hh.kz по ключевому слову и рассылки пользователям с
помощью telegram-бота.
Telegram-бот содержит админ-панель с авторизацией, где администратор канала может задать такие параметры как:
ключевое слово для поиска вакансий, время сканирования, состояние бота (вкл./откл.) и т.д.
Программа также имеет взаимодействие с БД для хранения данных вакансиях и пользователях telegram-бота.


Данный модуль является основным. Проект состоит из пяти модулей:
1. main.py - содержит точку входа программы, также здесь реализовано автоматическое переподключение в случае
отключения сети и логирование ошибкок в файл logs.txt.
2. bot.py - содержит функции для отправки сообщений пользователям, а также содержит функционал админ-панели бота.
3. config.py - содержит конфиденциальные данные о telegram-боте.
4. parsing.py - содержит функции для парсинга веб-страниц.
5. db.py - содержит функции для создания таблиц, сохранения и чтения данных из БД.

Программа выполняет следующие шаги:
1. Сохранение страниц в виде html-файлов в папку selenium_data через функцию 'save_pages'.
2. Парсинг сохраненных страниц и сохранение данных о всех найденных вакансиях по данному запросу.
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
Чтобы войти в админ-панель, введите '/admin'.
"""
from datetime import datetime
import threading
from time import sleep

from bot import MessageSender


def main():
    error_was_here = False
    thr_is_alive = False
    while True:
        my_bot = MessageSender()
        try:
            if not thr_is_alive:
                t = threading.Thread(target=my_bot.send_message, name='thr-1')
                t.daemon = True  # Необходимо для принудительного завершения программы.
                t.start()
                thr_is_alive = t.is_alive()
                print(f'Thr-1 активен: {t.is_alive()}')
                print(f'Потоков: {threading.active_count()}')

            if error_was_here is True:
                my_bot.send_error()

            my_bot.run()

        except Exception as e:
            print(f'Произошла ошибка: {str(e)}')

            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open('logs.txt', 'a', encoding='UTF-8') as f:
                f.write(f'{date}: {e}\n')

            error_was_here = True

            sleep(2)
            for i in range(10, 0, -1):
                print(f'Переподключение через... {i}.')
                sleep(1)


if __name__ == '__main__':
    main()




