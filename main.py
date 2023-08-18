
import json
import os.path
from time import sleep
from random import randrange
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
# from deepdiff import DeepDiff
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from fake_useragent import UserAgent
# from selenium.webdriver.chrome.options import Options


def get_url(p):
    return f'https://hh.kz/search/vacancy?text=python&salary=&no_magic=true&ored_clusters=true&' \
           f'order_by=publication_time&enable_snippets=true&excluded_text=&area=160&page={p}'


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
        sleep(5)

    for i in range(1, page_numbers + 1):
        try:
            driver.get(f'https://hh.kz/search/vacancy?text=python&salary=&no_magic=true&ored_clusters=true&'
                       f'order_by=publication_time&enable_snippets=true&excluded_text=&area=160&page={i-1}')
            sleep(randrange(3, 5))
            with open(f'selenium_data/page_{i}.html', 'w', encoding='utf-8') as file:
                file.write(driver.page_source)
                print(f'Страница {i} сохранена.')
                sleep(randrange(3, 5))
                #sleep(500)
        except Exception as ex:
            print(ex)
        finally:
            pass

    driver.close()
    driver.quit()


def get_data(lst_json):
    g_count = 0
    global page_numbers
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
                            sleep(1)
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

    lst_telegram = []
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
        print(f'Всего записей в БД: {len(all_data_json)}')
        with open("lst_all_data.json", "w", encoding="UTF-8") as file:
            json.dump(all_data_json, file, indent=4, ensure_ascii=False)

    if not lst_telegram:
        print('Новых постов нет.')
    else:
        print(f'Новые записи: {lst_telegram}')

    return lst_telegram


page_numbers = None


def main(headers, driver):
    lst_json = []
    save_pages(headers, driver)
    get_data(lst_json)
    data_for_telegram = get_telegram_data(lst_json)
    return data_for_telegram


def run_parser():
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/115.0.0.0 Safari/537.36'
    }

    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    options.add_argument(f"accept={headers['Accept']}")
    options.add_argument(f"user-agent={headers['User-Agent']}")
    driver = webdriver.Chrome(options=options)

    return main(headers, driver)


if __name__ == '__main__':
    run_parser()




