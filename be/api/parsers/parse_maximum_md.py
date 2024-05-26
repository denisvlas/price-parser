
import requests
from bs4 import BeautifulSoup
import json
from utils import extract_numbers  
from utils import reformat_image  
from utils import data_numbers  
from request_headers import headers

def parse_maximum_md(url):
  
 
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    print(f"Request to {url} returned status code {res.status_code}")
    res.encoding = res.apparent_encoding

    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.content, 'html.parser')
   
    data = []

    container = soup.select('div.js-content:not(.notification-product)')

    for el in container[:data_numbers]:
        link_element = el.find('div',class_='product__item__image').find('a').find('img',class_='lazy-load')
        if link_element and link_element.has_attr('data-src'):
                        image = link_element['data-src']
        if not link_element:
            continue
        title=el.find('div',class_='product__item__title').find('a').text
        link=el.find('div',class_='product__item__title').find('a')['href']
        link="https://maximum.md"+link
        lastPrice=extract_numbers(el.find('div',class_='product__item__price__block').find("div",class_="product__item__price-stats").find('div',class_='product__item__price-old').find('span').text)
        price=extract_numbers(el.find('div',class_='product__item__price__block').find("div",class_="product__item__price-stats").find('div',class_='product__item__price-current').find('span').text)
        
        
        product = {
            "name": title,
            "price": price,
            "image": image,
            "discount": lastPrice-price if lastPrice is not None else None,
            "stockOut": False,
            "lastPrice": lastPrice,
            "link": link,
            "shop": "maximum_md"
        }
        data.append(product)

    return data