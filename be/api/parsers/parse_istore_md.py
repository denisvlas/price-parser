
import requests
from bs4 import BeautifulSoup
import json
from utils import extract_numbers, reformat_image, data_numbers
from request_headers import headers

def parse_istore_md(url):
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    print(f"Request to {url} returned status code {res.status_code}")
    res.encoding = res.apparent_encoding

    soup = BeautifulSoup(res.content, 'html.parser')
    
    container = soup.find_all('div', class_="col-6 col-sm-6 col-md-4 col-lg-3 mb-2 mb-sm-2 mb-md-3 px-1 px-sm-1 px-md-2 mb-md-3")
    if not container:
        print(f"No products found - {url}")
        return []

    data = []

    for el in container[:data_numbers]:
        link_element = el.find('div').find('a', class_="stretched-link")
        if not link_element:
            continue
        
        image_element = el.find('div', class_='block-img').find('span').find('img')
        image = image_element.get('src', '') if image_element else None

        data_ga4 = link_element.get('data-ga4', '')
        if data_ga4:
            try:
                ga4_json = json.loads(data_ga4)
                item_data = ga4_json.get('ecommerce', {}).get('items', [{}])[0]
                title = item_data.get('item_name', '').strip()
                price = item_data.get('price', None)
                discount = item_data.get('discount', 0)
            except json.JSONDecodeError:
                title = ''
                price = None
                discount = 0
        else:
            title = ''
            price = None
            discount = 0

        price_element = el.find(class_='price-new')
        if price_element:
            price = extract_numbers(price_element.get_text().strip())

        discount_element = el.find(class_='difprice aclas')
        if discount_element:
            discount = extract_numbers(discount_element.get_text().strip())

        stock_out = 'stock_out' in el.get('class', [])
        
        product = {
            "name": title,
            "price": price,
            "image": image,
            "discount": -1 * discount,
            "stockOut": stock_out,
            "lastPrice": (price - discount) if price is not None else None,
            "link": link_element.get('href', ''),
            "shop": "istore.md"
        }
        data.append(product)

    return data
