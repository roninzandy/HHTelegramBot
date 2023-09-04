from datetime import datetime
import os.path
from time import sleep
from random import randrange
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

import db


def save_pages(headers, driver):
    """
      Функция сохраняет тестовую (первую) страницу сайта для определения количества страниц по данному запросу,
      формирует ссылки на страницы в цикле, а затем сохраняет все страницы в папку "selenium_data".

    """
    # Сохранение тестовой (первой) страницы и формирование переменной с количеством страниц page_numbers.
    p = 0  # Номер первой страницы
    url = f'https://almaty.hh.kz/search/vacancy?text=python&salary=&no_magic=true&ored_clusters=true&' \
          f'order_by=publication_time&enable_snippets=true&excluded_text=&area=160&page={p}'
    response = requests.get(url=url, headers=headers)
    src = response.text

    with open('selenium_data/test.html', 'w', encoding='utf-8') as file:
        file.write(src)

    with open('selenium_data/test.html', encoding='utf-8') as file:
        src = file.read()
        soup = BeautifulSoup(src, 'lxml')
        page_numbers = int(list(soup.find('div', class_='pager'))[-2].text)
        print(f'Всего страниц по данному запросу: {page_numbers}')
        sleep(randrange(3, 5))

    # Сохранение всех страниц сайта по данному запросу.
    for i in range(1, page_numbers + 1):
        try:
            driver.get(f'https://almaty.hh.kz/search/vacancy?text=python&salary=&no_magic=true&ored_clusters=true&'
                       f'order_by=publication_time&enable_snippets=true&excluded_text=&area=160&page={i-1}')
            sleep(randrange(3, 5))
            with open(f'selenium_data/page_{i}.html', 'w', encoding='utf-8') as file:
                file.write(driver.page_source)
                print(f'Страница {i} сохранена.')
                sleep(randrange(3, 5))
        except Exception as e:
            print(e)

    driver.close()
    driver.quit()

    return page_numbers


def get_data(lst_json, page_numbers):
    """
     Функция создает словари с данными о вакансиях и помещает их в список lst_json.
    """

    g_count = 0
    total_amount_of_posts = 0
    for j in range(1, page_numbers + 1):
        loop_count = 0
        with open(f'selenium_data/page_{j}.html', encoding='utf-8') as file:
            src_data = file.read()
            print('_' * 20)
            print(f'Начинается сбор данных со страницы {j}.')
            print('_'*20)
            soup_data = BeautifulSoup(src_data, 'lxml')
            data = soup_data.find_all('div', class_='vacancy-serp-item-body__main-info')
            for d in data:

                try:
                    title = d.find('a', class_='serp-item__title').text
                    title = title.replace('\u202F', ' ').replace('\u00A0', ' ')
                except Exception:
                    title = 'Должность не указана'

                try:
                    salary = d.find('span', class_='bloko-header-section-2').text
                    salary = salary.replace('\u202F', ' ').replace('\u00A0', ' ')
                except Exception:
                    salary = 'Зарплата не указана'

                try:
                    company = d.find('a', class_='bloko-link').text
                    company = company.replace('\u202F', ' ').replace('\u00A0', ' ')
                except Exception:
                    company = 'Компания не указана'

                try:
                    location = d.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
                    location = location.split(',')[0].replace('\u202F', ' ').replace('\u00A0', ' ')
                except Exception:
                    location = 'Место работы не указано'

                try:
                    link = d.find('a', class_='serp-item__title').get('href')
                except Exception:
                    link = 'Ссылка не указана'

                try:
                    img_soup = d.find('img', class_='vacancy-serp-item-logo')
                    url = img_soup.get('src')

                    try:
                        image_name = url.split('/')[-1]
                        if not os.path.exists(f'static/{image_name}'):
                            response = requests.get(url=url)
                            image_content = response.content
                            image_filename = os.path.join('static', image_name)

                            if not os.path.exists('static'):
                                os.makedirs('static')

                            with open(image_filename, 'wb') as f:
                                f.write(image_content)
                                print(f'Изображение {image_name} сохранено')
                            sleep(5)
                        img = image_name

                    except Exception:
                        img = 'Ошибка загрузки изображения'

                except Exception:
                    img = 'Изображение отсутствует'

                g_count += 1
                loop_count += 1
                if loop_count == 1:
                    total_amount_of_posts += len(data)

                print(f'Обрабатывается запись: {g_count}/{total_amount_of_posts}')
                # print('#' * 20)
                # print(title)
                # print(salary)
                # print(company)
                # print(location)
                # print(link)
                # print('#'*20)

                lst_json.append(

                    {
                        'Title': title,
                        'Salary': salary,
                        'Company': company,
                        'Location': location,
                        'Link': link,
                        'Image': img
                    }
                )


def get_telegram_data(lst_json):
    """
     Функция формирует данных о новых вакансиях, которые будут отправлены телеграм-ботом,
     а также записывает новые данные в БД.
    """

    lst_telegram = []
    if not os.path.exists('database.db'):
        if lst_json:
            db.create_table(lst_json)
    else:
        rows = db.select_data()
        for item in lst_json:
            found = False
            for row in rows:
                if item == row:
                    found = True
            if found is False:
                print('Идет запись...')
                lst_telegram.append(item)
        print(f'Всего записей в БД: {len(rows)+len(lst_telegram)}')

    if lst_telegram:
        print('Новые записи:')
        for item in lst_telegram:
            print(item)
        db.insert_data(lst_telegram)
        print(f'Всего новых записей: {len(lst_telegram)}')
    else:
        print('Новых записей нет.\n'
              f'Дата сканирования: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    return lst_telegram


def run_parsing():
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/115.0.0.0 Safari/537.36'
    }

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument(f"accept={headers['Accept']}")
    options.add_argument(f"user-agent={headers['User-Agent']}")
    driver = webdriver.Chrome(options=options)

    lst_json = []

    #pn = save_pages(headers, driver)  # pn - количество страниц сайта по данному запросу.
    pn = 5
    get_data(lst_json, pn)
    data_for_telegram = get_telegram_data(lst_json)

    return data_for_telegram  # Передача данных о вакансиях телеграм-боту в виде списка с вложенными словарями.




