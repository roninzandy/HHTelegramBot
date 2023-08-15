from time import sleep

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent

# url = 'https://hh.kz/search/vacancy?no_magic=true&L_save_area=true&text=python&excluded_text=&area=160&salary=&currency_code=KZT&experience=doesNotMatter&order_by=publication_time&search_period=0&items_on_page=100'
#
# ua = UserAgent(browsers=['edge', 'chrome', 'firefox'])
# options = webdriver.ChromeOptions()
# options.add_argument(f"user-agent={ua.random}")
# driver = webdriver.Chrome(options=options)
#
# i=4
# try:
#     driver.get(f'https://hh.kz/search/vacancy?text=python&salary=&no_magic=true&ored_clusters=true&order_by=publication_time&enable_snippets=true&excluded_text=&area=160&page={i}')
#     sleep(5)
#     with open(f'selenium_data/page_{i+1}.html', 'w', encoding='utf-8') as file:
#         file.write(driver.page_source)
#         print(f'Страница {i+1} сохранена.')
#         sleep(5)
# except Exception as ex:
#     print(ex)
# finally:
#     driver.close()
#     driver.quit()


# headers = {
#     'Accept': '*/*',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
# }
#
# response = requests.get(url=url, headers=headers)
# src = response.text
#
# with open('test.html', 'w', encoding='utf-8') as file:
#     file.write(src)

def get_data():
    with open('test.html', encoding='utf-8') as file:
        src = file.read()
        soup = BeautifulSoup(src, 'lxml')

        page_numbers = int(list(soup.find('div', class_='pager'))[-2].text)
        print(page_numbers)

        pages = [page for page in range(page_numbers)]
        print(pages)

        urls = {}
        url = 'https://hh.kz/search/vacancy?no_magic=true&L_save_area=true&text=python&excluded_text=&area=160&salary=&currency_code=KZT&experience=doesNotMatter&order_by=publication_time&search_period=0&items_on_page=100&page='
        for page in range(len(pages)):
            urls[page+1] = f'{url}{page}'
        print(urls)

        g_count = 0
        #for key, value in urls.items():
        for key in range(5):
            print(key)

            # response = requests.get(url=value, headers=headers)
            # src = response.text
            # with open(f'data/page_{key}.html', 'w', encoding='utf-8') as file:
            #     file.write(src)
            #     print(f'Страница {key} сохранена.')
            #with open(f'selenium_data/page_{key}.html', encoding='utf-8') as file:
            with open(f'selenium_data/page_{key+1}.html', encoding='utf-8') as file:
                src = file.read()
                #print(f'Начинается сбор данных со страницы {key + 1}.')
                print(f'Начинается сбор данных со страницы {key+1}.')
                print('_'*20)
                soup = BeautifulSoup(src, 'lxml')
                data = soup.find_all('div', class_='vacancy-serp-item-body__main-info')
                for d in data:

                    try:
                        title = d.find('a', class_='serp-item__title').text
                    except Exception as ex:
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

                    print(f'Обрабатывается запись: {g_count}')
                    print('#' * 20)
                    print(title)
                    print(salary)
                    print(company)
                    print(location)
                    print('#'*20)
                    g_count += 1
                    #time.sleep(1)

def main():
    get_data()

if __name__ == '__main__':
   main()

    #всего вакансий: 225


