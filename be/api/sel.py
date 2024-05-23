from flask import Flask, request, jsonify
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import re
import json
app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Flask Parsing Server!"

@app.route('/parse_all', methods=['POST'])
def get_all_data():
    search = request.json.get('search')
    page = request.json.get('page', 1)  # Default page 1 if not provided
    search += "&page=" + str(page)
    
    if not search:
        return jsonify({"error": "No search query provided"}), 400
    
    print(search)
    
    aggregated_results = []

    for store, parser_data in store_parsers.items():
        url = parser_data['url'] + search
        parsed_data = parser_data['parser'](url)
        aggregated_results.extend(parsed_data)

    # Example filtering function
    # aggregated_results = get_filtered_projects('Scumpe', list(aggregated_results))

    return jsonify(aggregated_results)

def parse_darwin(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'card-product')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
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
    
    finally:
        driver.quit()

def parse_enter(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'grid-item')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
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
    
    finally:
        driver.quit()


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


def extract_numbers(price_str):
    return int(''.join(re.findall(r'\d+', price_str)))

store_parsers = {
    'darwin': {
        'url': 'https://darwin.md/search?search=',
        'parser': parse_darwin
    },
    'enter': {
        'url': 'https://enter.online/search?query=',
        'parser': parse_enter
    }
}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
