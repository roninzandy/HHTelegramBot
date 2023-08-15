import requests
from bs4 import BeautifulSoup

url = 'https://hh.kz/search/vacancy?area=160&enable_snippets=true&excluded_text=&no_magic=true&ored_clusters=true&text=python&order_by=publication_time'
headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

response = requests.get(url=url, headers=headers)
src = response.text

with open('test.html', 'w', encoding='utf-8') as file:
    file.write(src)

def get_data():
    with open('test.html', encoding='utf-8') as file:
        src = file.read()
        soup = BeautifulSoup(src, 'lxml')

        page_numbers = int(list(soup.find('div', class_='pager'))[-2].text)
        print(page_numbers)

        pages = [page for page in range(page_numbers)]
        print(pages)

        urls = {}
        url = 'https://hh.kz/search/vacancy?area=160&enable_snippets=true&excluded_text=&no_magic=true&ored_clusters=true&text=python&order_by=publication_time&page='
        for page in range(len(pages)):
            urls[page+1] = f'{url}{page}'
        print(urls)

        for key, value in urls.items():
            response = requests.get(url=value, headers=headers)
            src = response.text
            with open(f'data/page_{key}.html', 'w', encoding='utf-8') as file:
                file.write(src)
                print(f'Страница {key} сохранена.')
def main():
    get_data()

if __name__ == '__main__':
    main()


