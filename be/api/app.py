from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import re
from flask_cors import CORS
import json
import time
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    print("Hello")
    return "Welcome to the Flask Parsing Server!"

@app.route('/parse_all', methods=['POST'])
def get_all_data():
    search = request.json.get('search')
    search+="&page="+str(request.json.get('page'))
    if not search:
        return jsonify({"error": "No search query provided"}), 400
    print(search)
    search = search.replace(' ', '%20')
    # print(search)
    print(store_parsers['darwin']['url'] + search)
    print(store_parsers['enter']['url'] + search)
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(store_parsers[store]['parser'], store_parsers[store]['url'] + search) for store in store_parsers]
        results = [future.result() for future in futures]
    aggregated_results = [item for sublist in results for item in sublist]

    print(len(jsonify(aggregated_results).get_json()))
    
    aggregated_results=get_filtered_projects('Scumpe', list(aggregated_results))
    return aggregated_results   

def parse_darwin(url):
    res = requests.get(url)
    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    data = []

    figures = soup.find_all('figure', class_='card card-product border-0')
    for figure in figures[:5]:
        time.sleep(1)
        # Extracting data from the <a> tag inside each <figure>
        link_element = figure.find('a', class_='ga-item')
        if not link_element:
            continue
        
        # Extracting data from data-ga4 attribute
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
        
        # Extracting data from other elements within <figure>
        price_element = figure.find(class_='price-new')
        price = extract_numbers(price_element.get_text().strip()) if price_element else price
        
        image_element = figure.find('img', class_='card-image')
        image = image_element.get('src', '') if image_element else None
        
        discount_element = figure.find(class_='difprice aclas')
        discount = extract_numbers(discount_element.get_text().strip()) if discount_element else discount
        
        # Check if the product is out of stock
        stock_out = 'stock_out' in figure.get('class', [])
        if image:
            image = image.replace('.png', '.webp')
            image = image.replace('.jpg', '.webp')
            image = image.replace('.jpeg', '.webp')
        # Constructing the product dictionary
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

def extract_numbers(price_str):
    # Extract all digits and join them into a single string
    return int(''.join(re.findall(r'\d+', price_str)))


def extract_numbers(price_str):
    # Extract all digits and join them into a single string
    return int(''.join(re.findall(r'\d+', price_str)))

def parse_other_store(url):
    res = requests.get(url)
    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    data = []

    titles = soup.find_all(class_="another-title-class")
    prices = soup.find_all(class_="another-price-class")
    images = soup.find_all(class_="another-image-class")

    for title, price, image in zip(titles, prices, images):
        product = {
            "product": title.get_text().strip(),
            "price": price.get_text().strip(),
            "image": image.get('src', '')
        }
        data.append(product)

    return data


# def parse_enter(url):
#     res = requests.get(url)
#     if res.status_code != 200:
#         return []

#     soup = BeautifulSoup(res.text, 'html.parser')
#     data = []

#     product_elements = soup.find_all('a', attrs={'data-info_wrap': 'true'})

#     for product in product_elements:
#         title_element = product.find('span', class_='product-title')
#         price_element = product.get('data-ga4')
#         image_element = product.find('img')
#         discount_element = product.get('data-ga4')

#         title = title_element.get_text().strip() if title_element else 'No title'
#         image = image_element['data-src'] if image_element and 'data-src' in image_element.attrs else None
#         price = None
#         discount = 0
#         if image:
#             image = image.replace('.png', '.webp')
#             image = image.replace('.jpg', '.webp')
#             image = image.replace('.jpeg', '.webp')


#         if price_element:
#             price_data = json.loads(price_element)
#             if 'ecommerce' in price_data and 'value' in price_data['ecommerce']:
#                 price = price_data['ecommerce']['value']
#             if 'ecommerce' in price_data and 'items' in price_data['ecommerce'] and len(price_data['ecommerce']['items']) > 0:
#                 discount = price_data['ecommerce']['items'][0].get('discount', 'No discount')

#         product_data = {
#             "name": title,
#             "price": price,
#             "image": image,
#             "discount": discount,
#             "shop": "enter"
#         }
#         data.append(product_data)

#     return data


def parse_enter(url):
    res = requests.get(url)
    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    data = []

    figures = soup.find_all('div', class_='grid-item')
    for figure in figures[:5]:
        time.sleep(1)
        # Extracting data from the <a> tag inside each <figure>
        link_element = figure.find('a')
        if not link_element:
            continue
        
        # Extracting data from data-ga4 attribute
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
        
        # Extracting data from other elements within <figure>
        price_element = figure.find(class_='price-new')
        price = extract_numbers(price_element.get_text().strip()) if price_element else price
        

        image_element = link_element.find('span', class_='loading-img')
        image = image_element.find('img')

        image = image.get('data-src', '') if image_element else None
        
        discount_element = figure.find(class_='difprice aclas')
        discount = extract_numbers(discount_element.get_text().strip()) if discount_element else discount
        
        # Check if the product is out of stock
        stock_out = 'no-stock' in figure.get('class', [])
        if image:
            image = image.replace('.png', '.webp')
            image = image.replace('.jpg', '.webp')
            image = image.replace('.jpeg', '.webp')
        # Constructing the product dictionary
        product = {
            "name": title,
            "price": price,
            "image": image,
            "discount": discount,
            "stockOut": stock_out,
            "lastPrice": price + discount if price is not None else None,
            "link": link_element.get('href', ''),
            "shop": "enter"
        }
        data.append(product)

    return data
@app.route('/filter', methods=['POST'])
def get_filtered_projects(filter_value=None, data=None):
    # Extrage datele din corpul cererii JSON
    if data is None and filter_value is None:
        data = request.json.get('data')
        filter_value = request.json.get('filter')

    # Implementează filtrarea pe baza datelor și filtrului primit
    # Exemplu simplu de filtrare, modifică după nevoie
    if filter_value == 'Ieftine':
        data.sort(key=lambda x: x.get('price', 0))
    if filter_value == 'Scumpe':
        data.sort(key=lambda x: x.get('price', 0), reverse=True)  
    if filter_value == 'Reduceri':
        data.sort(key=lambda x: x.get('discount', 0), reverse=True)  

    return jsonify(data)


@app.route('/test_request', methods=['GET'])
def test_request():
    res = requests.get('https://api.github.com')
    return jsonify({"status_code": res.status_code, "response": res.json()})


# Dicționar pentru a mapa numele magazinului la funcția de parsing corespunzătoare
store_parsers = {
    'darwin': {
        'url': 'https://darwin.md/search?search=',
        'parser': parse_darwin
    },
    'enter': {
        'url': 'https://enter.online/search?query=',
        'parser': parse_enter
    }
    # Adaugă aici alte magazine cu funcțiile lor de parsing
}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


