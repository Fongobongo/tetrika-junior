import csv
import requests
from bs4 import BeautifulSoup

def scrape_animals():

    wiki_address = 'https://ru.wikipedia.org'

    next_page = '/wiki/Категория:Животные_по_алфавиту'

    beasts_dict = {}

    i = 1

    while next_page is not None:

        status_code = 0

        while status_code != 200:

            r = requests.get(wiki_address + next_page, headers={'User-Agent': 'Mozilla/5.0'})
            status_code = r.status_code

            soup = BeautifulSoup(r.text, 'html.parser')

            beasts = soup.select('div.mw-category.mw-category-columns ul')

            current_page_beasts = [beast.get_text() for ul in beasts for beast in ul.find_all('a')]
            print(f'Звери со страницы № {i}: {current_page_beasts}')

            for beast in current_page_beasts:
                letter = beast[0].upper()
                beasts_dict[letter] = beasts_dict.setdefault(letter, 0) + 1

            next_page = soup.find('a', string='Следующая страница')

            if next_page is not None:
                next_page = next_page.get('href')
                i += 1

    with open('beasts.csv', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        for letter, count in beasts_dict.items():
            writer.writerow([letter, count])
        print(f'Звери подсчитаны на {i} страницах и записаны в файл beasts.csv')


if __name__ == '__main__':
    scrape_animals()