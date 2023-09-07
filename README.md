# HHTelegramBot
Программа HHTelegramBot предназначена для парсинга данных о новых вакансиях с сайта hh.kz и рассылки пользователям с помощью telegram-бота. 
Данная программа создана для тех, кто ищет работу в сфере backend-разработки на Python. Функционал программы включает в себя:
- сохранение найденных HTML-страниц по данному запросу;
- сохранение данных о вакансиях, полученных в результате парсинга, в БД;
- отправку пользователям новых вакансий;
- расширенная админ-панель с авторизацией, которая позволяет задать такие параметры как: ключевое слово для поиска вакансий, время сканирования, состояние бота (вкл./откл.) и т.д.;
- ведения журнала ошибок и уведомление администраторов бота в случае ошибки;

Для активации telegram-бота добавьте его в telegram по имени @beastchargerbot (https://t.me/beastchargerbot).
Чтобы войти в админ-панель, введите '/admin'.

Более подробную информацию можно найти в модуле main.py, который является основным.

Автор: Подколзин Андрей
Тел.: 8 (705) 529-86-25
E-mail: suddenlyandy@gmail.com
