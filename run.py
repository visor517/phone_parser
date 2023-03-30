import json
import os
import requests

from bs4 import BeautifulSoup

from timezones import TIMEZONE_BY_REGION


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"}

# собираем страницы
for code in range(900, 1000):
    url = f"https://www.kody.su/mobile/{code}"
    response = requests.get(url, headers=headers)
    dom = BeautifulSoup(response.text, "html.parser")

    if (data_table := dom.find("table", {"class": "tbnum"})) is None:
        print(f'Нет страницы {url}')
        continue

    items = data_table.find_all("tr")

    result = []
    for item in items[1:]:
        # собираем данные объекта
        b = item.find_all("td")
        interval, operator, region = [td.getText().strip() for td in item.find_all("td")]

        interval = interval.replace(f"{code}-", "")
        if len(interval) == 7:
            interval_from = interval.replace("x", "0")
            interval_to = interval.replace("x", "9")
        else:
            interval_from = interval[:7].replace("x", "0")
            interval_to = interval[-7:].replace("x", "9")

        timezone = TIMEZONE_BY_REGION.get(region)
        if not TIMEZONE_BY_REGION.get(region):
            print(f"Новый регион - {region}")

        if region in ["Москва", "Санкт-Петербург"]:
            city = region
            region = None
        else:
            city = None

        # заполняем объект
        item_obj = {
            "code": code,
            "from": interval_from,
            "to": interval_to,
            "operator": operator,
            "region": region,
            "city": city,
            "district": None,
            "timezone": timezone,
        }
        result.append(item_obj)

    # сохранение результатов
    if not os.path.exists("results"):
        os.makedirs("results")
    with open(f'results/DEF-9xx.json', 'w', encoding='UTF-8') as file:
        file.write(json.dumps(result, ensure_ascii=False))
