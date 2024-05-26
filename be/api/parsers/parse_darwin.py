
import requests
from bs4 import BeautifulSoup
import json
from utils import extract_numbers  
from utils import data_numbers  
from utils import reformat_image  

def parse_darwin(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }
 
    res = requests.get(url, headers=headers, verify=False)

    print(f"Request to {url} returned status code {res.status_code}")

    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    data = []

    figures = soup.find_all('figure', class_='card card-product border-0')
    for figure in figures[:data_numbers]:
        link_element = figure.find('a', class_='ga-item')
        if not link_element:
            continue
        
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
        
        price_element = figure.find(class_='price-new')
        price = extract_numbers(price_element.get_text().strip()) if price_element else price
        
        image_element = figure.find('img', class_='card-image')
        image = image_element.get('src', '') if image_element else None
        
        discount_element = figure.find(class_='difprice aclas')
        discount = extract_numbers(discount_element.get_text().strip()) if discount_element else discount
        
        stock_out = 'stock_out' in figure.get('class', [])
        if image:
          image=reformat_image(image)
        
        product = {
            "name": title,
            "price": price,
            "image": image,
            "discount": discount,
            "stockOut": stock_out,
            "lastPrice": price + discount if price is not None else None,
            "link": link_element.get('href', ''),
            "shop": "darwin"
        }
        data.append(product)

    return data