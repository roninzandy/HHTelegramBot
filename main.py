from time import sleep

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

options = webdriver.ChromeOptions()
options.add_argument(f'--headers="{headers}"')
driver = webdriver.Chrome(options=options)
options.add_argument(f"user-agent={headers['User-Agent']}")
def get_url(p):
    return f'https://hh.kz/search/vacancy?text=python&salary=&no_magic=true&ored_clusters=true&order_by=publication_time&enable_snippets=true&excluded_text=&area=160&page={p}'
response = requests.get(url=get_url(0), headers=headers)

src = response.text
with open('test.html', 'w', encoding='utf-8') as file:
    file.write(src)

with open('test.html', encoding='utf-8') as file:
    src = file.read()
    soup = BeautifulSoup(src, 'lxml')

    page_numbers = int(list(soup.find('div', class_='pager'))[-2].text)
    print(f'Всего страниц по данному запросу: {page_numbers}')

for i in range(1, page_numbers + 1):
    try:
        driver.get(f'https://hh.kz/search/vacancy?text=python&salary=&no_magic=true&ored_clusters=true&order_by=publication_time&enable_snippets=true&excluded_text=&area=160&page={i-1}')
        sleep(5)
        with open(f'selenium_data/page_{i}.html', 'w', encoding='utf-8') as file:
            file.write(driver.page_source)
            print(f'Страница {i} сохранена.')
            sleep(5)
    except Exception as ex:
        print(ex)
    finally:
        pass

driver.close()
driver.quit()

def get_data():
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
                    title = d.find('a', class_='serp-item__title').text
                except:
                    title = 'Должность не указана'

                try:
                    salary = d.find('span', class_='bloko-header-section-2').text
                except Exception as ex:
                    salary = 'Зарплата не указана'

                try:
                    company = d.find('a', class_='bloko-link').text
                except Exception as ex:
                    company = 'Компания не указана'

                try:
                    location = d.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text.split(',')[0]
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

                #time.sleep(1)

def main():
    get_data()

if __name__ == '__main__':
   main()



