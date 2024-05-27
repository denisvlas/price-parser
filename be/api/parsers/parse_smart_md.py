


import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from flask import Flask, request, jsonify
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from utils import extract_numbers, reformat_image, data_numbers
from request_headers import headers

def parse_smart_md(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument(f"user-agent={headers['User-Agent']}")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        return []

    data = []
    
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-results')))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.find_all('div', class_='search-item search-product custom_product_content')
        if not items:
            print(f"No products found - {url}")
            return []

        for item in items[:data_numbers]:
            try:
                link_element = item.find('div', class_='custom_product_title').find('a')
                if not link_element:
                    continue
                link = link_element['href']
                
                img_element = item.find('div', class_='custom_product_container').find('div', class_='custom_product_image').find('a').find('img')
                if not img_element:
                    continue
                img = img_element['src']
                
                title = link_element.text
                
                price_container = item.find('div', class_='custom_product_prices').find('a').find('div', class_='custom_product_price')
                last_price_element = price_container.find('span', class_='special')
                last_price = extract_numbers(last_price_element.text) if last_price_element else None
                
                current_price_element = price_container.find('span', class_='regular')
                if not current_price_element:
                    continue
                price = extract_numbers(current_price_element.text)
                
                discount = last_price - price if last_price else 0
                
                product = {
                    "name": title,
                    "price": price,
                    "image": img,
                    "discount": discount,
                    "stockOut": None,
                    "lastPrice": last_price,
                    "link": link,
                    "shop": "smart.md"
                }
                data.append(product)

            except AttributeError as e:
                print(f"Error parsing item: {e}")
                continue
     
    finally:
        driver.quit()  # Ensure the browser is closed even if an error occurs

    return data
