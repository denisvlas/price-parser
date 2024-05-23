from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import re
from flask_cors import CORS
import json
import random 
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    print("Hello")
    return "Welcome to the Flask Parsing Server!"

@app.route('/parse_all', methods=['POST'])
def get_all_data():
    search = request.json.get('search')
    search += "&page=" + str(request.json.get('page'))
    if not search:
        return jsonify({"error": "No search query provided"}), 400
    print(search)
    search = search.replace(' ', '%20')
    print(store_parsers['darwin']['url'] + search)
    print(store_parsers['enter']['url'] + search)
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(store_parsers[store]['parser'], store_parsers[store]['url'] + search) for store in store_parsers]
        results = [future.result() for future in futures]
    aggregated_results = [item for sublist in results for item in sublist]

    print(len(jsonify(aggregated_results).get_json()))
    
    aggregated_results = get_filtered_projects('Scumpe', list(aggregated_results))
    return aggregated_results

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
    for figure in figures[:5]:
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
            image = image.replace('.png', '.webp')
            image = image.replace('.jpg', '.webp')
            image = image.replace('.jpeg', '.webp')
        
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
    return int(''.join(re.findall(r'\d+', price_str)))



def parse_enter(url):
    
    user_agents_list = [
        'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
    ]

    headers = {
        'User-Agent': random.choice(user_agents_list),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
    }

    session = requests.Session()
    res = session.get(url, headers=headers)


    res = requests.get(url, headers={'User-Agent': random.choice(user_agents_list)})
    
    # res = requests.get(url, headers=headers)
    print(f"Request to {url} returned status code {res.status_code}")

    if res.status_code != 200:
        return []

    soup = BeautifulSoup(res.text, 'html.parser')
    data = []

    figures = soup.find_all('div', class_='grid-item')
    for figure in figures[:5]:
        link_element = figure.find('a')
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
        
        image_element = link_element.find('span', class_='loading-img')
        image = image_element.find('img')
        image = image.get('data-src', '') if image_element else None
        
        discount_element = figure.find(class_='difprice aclas')
        discount = extract_numbers(discount_element.get_text().strip()) if discount_element else discount
        
        stock_out = 'no-stock' in figure.get('class', [])
        if image:
            image = image.replace('.png', '.webp')
            image = image.replace('.jpg', '.webp')
            image = image.replace('.jpeg', '.webp')
        
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

# def parse_enter(url):
#     user_agents_list = [
#         'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
#         'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
#         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
#     ]

#     headers = {
#         'User-Agent': random.choice(user_agents_list),
#         'Accept-Language': 'en-US,en;q=0.9',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#         'Connection': 'keep-alive',
#     }

#     session = requests.Session()
#     response = session.get(url, headers=headers)

#     print(f"Request to {url} returned status code {response.status_code}")

#     if response.status_code != 200:
#         return []

#     soup = BeautifulSoup(response.text, 'html.parser')
#     data = []

#     figures = soup.find_all('div', class_='grid-item')
#     for figure in figures[:5]:
#         link_element = figure.find('a')
#         if not link_element:
#             continue
        
#         data_ga4 = link_element.get('data-ga4', '')
#         if data_ga4:
#             try:
#                 ga4_json = json.loads(data_ga4)
#                 item_data = ga4_json.get('ecommerce', {}).get('items', [{}])[0]
#                 title = item_data.get('item_name', '').strip()
#                 price = item_data.get('price', None)
#                 discount = item_data.get('discount', 0)
#             except json.JSONDecodeError:
#                 title = ''
#                 price = None
#                 discount = 0
#         else:
#             title = ''
#             price = None
#             discount = 0
        
#         price_element = figure.find(class_='price-new')
#         price = extract_numbers(price_element.get_text().strip()) if price_element else price
        
#         image_element = link_element.find('span', class_='loading-img')
#         image = image_element.find('img')
#         image = image.get('data-src', '') if image_element else None
        
#         discount_element = figure.find(class_='difprice aclas')
#         discount = extract_numbers(discount_element.get_text().strip()) if discount_element else discount
        
#         stock_out = 'no-stock' in figure.get('class', [])
#         if image:
#             image = image.replace('.png', '.webp')
#             image = image.replace('.jpg', '.webp')
#             image = image.replace('.jpeg', '.webp')
        
#         product = {
#             "name": title,
#             "price": price,
#             "image": image,
#             "discount": discount,
#             "stockOut": stock_out,
#             "lastPrice": price + discount if price is not None else None,
#             "link": link_element.get('href', ''),
#             "shop": "enter"
#         }
#         data.append(product)

#     return data


@app.route('/filter', methods=['POST'])
def get_filtered_projects(filter_value=None, data=None):
    if data is None and filter_value is None:
        data = request.json.get('data')
        filter_value = request.json.get('filter')

    if filter_value == 'Ieftine':
        data.sort(key=lambda x: x.get('price', 0))
    if filter_value == 'Scumpe':
        data.sort(key=lambda x: x.get('price', 0), reverse=True)
    if filter_value == 'Reduceri':
        data.sort(key=lambda x: x.get('discount', 0), reverse=True)

    return jsonify(data)

store_parsers = {
    'darwin': {
        'url': 'https://94.158.246.177/search?search=',
        'parser': parse_darwin
    },
    'enter': {
        'url': 'https://enter.online/search?query=',
        'parser': parse_enter
    }
}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
