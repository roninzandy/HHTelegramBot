
import datetime


import json
import os.path
from time import sleep
from random import randrange
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from deepdiff import DeepDiff
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options



def get_url(p):
    return f'https://hh.kz/search/vacancy?text=python&salary=&no_magic=true&ored_clusters=true&order_by=publication_time&enable_snippets=true&excluded_text=&area=160&page={p}'

def save_pages(headers, driver):
    response = requests.get(url=get_url(0), headers=headers)
    src = response.text
    with open('test.html', 'w', encoding='utf-8') as file:
        file.write(src)

    with open('test.html', encoding='utf-8') as file:
        src = file.read()
        soup = BeautifulSoup(src, 'lxml')

        global page_numbers
        page_numbers = int(list(soup.find('div', class_='pager'))[-2].text)

        print(f'Всего страниц по данному запросу: {page_numbers}')

        sleep(3)


    for i in range(1, page_numbers + 1):
        try:
            driver.get(f'https://hh.kz/search/vacancy?text=python&salary=&no_magic=true&ored_clusters=true&order_by=publication_time&enable_snippets=true&excluded_text=&area=160&page={i-1}')
            sleep(randrange(3, 5))
            with open(f'selenium_data/page_{i}.html', 'w', encoding='utf-8') as file:

            #with open(f'selenium_data/page_{i}_{datetime.datetime.now().strftime("%Y-%m-%d %H-%M")}.html', 'w', encoding='utf-8') as file:

                file.write(driver.page_source)
                print(f'Страница {i} сохранена.')
                sleep(randrange(3, 5))
        except Exception as ex:
            print(ex)
        finally:
            pass


    # driver.close()
    # driver.quit()




def get_data(lst_json):
    g_count = 0
    global page_numbers
    for j in range(1, page_numbers + 1):

        with open(f'selenium_data/page_{j}.html', encoding='utf-8') as file:
            src_data = file.read()
            print(f'Начинается сбор данных со страницы {j}.')
            print('_'*20)
            soup_data = BeautifulSoup(src_data, 'lxml')
            data = soup_data.find_all('div', class_='vacancy-serp-item-body__main-info')
            for d in data:

                try:
                    title = d.find('a', class_='serp-item__title').text.replace('\u202F', ' ').replace('\u00A0', ' ')
                except:
                    title = 'Должность не указана'

                try:
                    salary = d.find('span', class_='bloko-header-section-2').text.replace('\u202F', ' ').replace('\u00A0', ' ')
                except Exception as ex:
                    salary = 'Зарплата не указана'

                try:
                    company = d.find('a', class_='bloko-link').text.replace('\u202F', ' ').replace('\u00A0', ' ')
                except Exception as ex:
                    company = 'Компания не указана'

                try:
                    location = d.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text.split(',')[0].replace('\u202F', ' ').replace('\u00A0', ' ')
                except Exception as ex:
                    location = 'Место работы не указано'

                g_count += 1
                print(f'Обрабатывается запись: {g_count}')
                print('#' * 20)
                print(title)
                print(salary)
                print(company)
                print(location)
                print('#'*20)

                lst_json.append(

                    {
                        'Title': title,
                        'Salary': salary,
                        'Company': company,
                        'Location': location
                    }
                )






def get_telegram_data(lst_json):

    lst_telegram = []  # -> lst[dict]
    if not os.path.exists("lst_all_data.json"):
        with open("lst_all_data.json", "w", encoding="UTF-8") as f:
            json.dump(lst_json, f, indent=4, ensure_ascii=False)
    else:
        with open("lst_all_data.json", encoding="UTF-8") as f:
            all_data_json = json.load(f)
            for i in lst_json:
                found = False
                for j in all_data_json:
                    if i == j:
                        found = True
                if found == False:
                    print('Идет запись...')
                    lst_telegram.append(i)
                    all_data_json.append(i)

    if lst_telegram:
        print("Текущее время:", datetime.datetime.now())
    else:
        print('Новых постов нет.')

    #перезапись файла-json с учетом новых записей
    with open("lst_all_data.json", "w", encoding="UTF-8") as file:
        json.dump(all_data_json, file, indent=4, ensure_ascii=False)

    return lst_telegram




page_numbers = None
def main(headers, driver):
    while True:
        lst_json = []
        save_pages(headers, driver)
        get_data(lst_json)
        data_for_telegram = get_telegram_data(lst_json)
        yield data_for_telegram
        sleep(60)

def run_parser():
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    options = webdriver.ChromeOptions()
    options.add_argument(f'--headers="{headers}"')
    options.add_argument(f"user-agent={headers['User-Agent']}")
    driver = webdriver.Chrome(options=options)

    data_generator = list(main(headers, driver))

    for data in data_generator:
        print("Sending data:", data)
    return data_generator

if __name__ == '__main__':
    run_parser()







