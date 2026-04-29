import json
import os
import requests
from time import sleep
from bs4 import BeautifulSoup
from timezones import TIMEZONE_BY_REGION

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"}

# Накопительный результат
result = []

# Обработка кодов от 900 до 999
for code in range(900, 1000):
    url = f"https://www.kody.su/mobile/{code}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        dom = BeautifulSoup(response.text, "html.parser")

        data_table = dom.find("table", {"class": "tbnum"})
        if data_table is None:
            print(f"Нет данных: {url}")
            continue

        rows = data_table.find_all("tr")
        found_records = 0

        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            interval, operator, region = [td.get_text(strip=True) for td in cells[:3]]

            # Обработка диапазона номеров
            interval = interval.replace(f"{code}-", "")
            if len(interval) == 7:
                interval_from = interval.replace("x", "0")
                interval_to = interval.replace("x", "9")
            else:
                interval_from = interval[:7].replace("x", "0")
                interval_to = interval[-7:].replace("x", "9")

            timezone = TIMEZONE_BY_REGION.get(region)
            if not timezone:
                print(f"Новый регион - {region}")

            if region in ["Москва", "Санкт-Петербург"]:
                city = region
                region = None
            else:
                city = None

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
            found_records += 1

        print(f"Обработано: {code} | Найдено диапазонов: {found_records}")

    except requests.RequestException as e:
        print(f"Ошибка запроса {url}: {e}")
    except Exception as e:
        print(f"Ошибка парсинга {url}: {e}")

    sleep(0.5)

# Сохранение результатов
if not os.path.exists("results"):
    os.makedirs("results")

output_file = "results/DEF-9xx.json"
with open(output_file, "w", encoding="UTF-8") as file:
    file.write(json.dumps(result, ensure_ascii=False, indent=2))

print(f"\nГотово! Сохранено {len(result)} диапазонов в {output_file}")
