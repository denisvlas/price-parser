

import requests
from bs4 import BeautifulSoup
import json
from utils import extract_numbers, reformat_image, data_numbers
from request_headers import headers

def parse_maximum_md(url):
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.content, 'html.parser')
    
    container = soup.select('div.js-content:not(.notification-product)')
    if not container:
        print(f"No products found - {url}")
        return []

    data = []
    
    for el in container[:data_numbers]:
        try:
            link_element = el.find('div', class_='product__item__image').find('a').find('img', class_='lazy-load')
            if link_element and link_element.has_attr('data-src'):
                image = link_element['data-src']
            else:
                continue

            title_element = el.find('div', class_='product__item__title').find('a')
            if not title_element:
                continue
            title = title_element.text
            link = "https://maximum.md" + title_element['href']

            price_block = el.find('div', class_='product__item__price__block').find('div', class_='product__item__price-stats')
            if not price_block:
                continue

            last_price_element = price_block.find('div', class_='product__item__price-old').find('span')
            last_price = extract_numbers(last_price_element.text) if last_price_element else None

            current_price_element = price_block.find('div', class_='product__item__price-current').find('span')
            if not current_price_element:
                continue
            price = extract_numbers(current_price_element.text)
            
            product = {
                "name": title,
                "price": price,
                "image": image,
                "discount": (last_price - price) if last_price else 0,
                "stockOut": False,
                "lastPrice": last_price,
                "link": link,
                "shop": "maximum.md"
            }
            data.append(product)

        except AttributeError as e:
            print(f"Error parsing element: {e}")
            continue

    return data
