
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from flask import Flask, request, jsonify
from webdriver_manager.chrome import ChromeDriverManager
from request_headers import headers
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from utils import extract_numbers
from utils import reformat_image

def parse_smart_md(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument(f"user-agent={headers['User-Agent']}")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    product = {
            "name": None,
            "price":None ,
            "image": None,
            "discount": None,
            "stockOut": None,
            "lastPrice": None,
            "link": None,
            "shop": None
        }
    data = []
    
    try:
        driver.get(url)
        time.sleep(5)  # Așteaptă ca pagina să se încarce complet (poate fi ajustată în funcție de necesități)

        # Extrage elementul dorit folosind Selenium
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-results')))
        container = driver.find_elements(By.CLASS_NAME, 'search-results')
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        items = soup.find_all('div', class_='search-item search-product custom_product_content')
        for item in items:
            link = item.find('div', class_='custom_product_title').find('a')['href']   
            img = reformat_image(item.find('div', class_='custom_product_container').find('div',class_='custom_product_image').find('a').find('img')['src'])
            title = item.find('div', class_='custom_product_title').find('a').text
            lastPrice = extract_numbers(item.find('div', class_='custom_product_prices').find('a').find('div', class_='custom_product_price').find('span',class_='special').text)
            price = extract_numbers(item.find('div', class_='custom_product_prices').find('a').find('div', class_='custom_product_price').find('span',class_='regular').text)
            discount=lastPrice-price
            
            product = {
                "name": title,
                "price":price ,
                "image": img,
                "discount": discount,
                "stockOut": None,
                "lastPrice": lastPrice,
                "link": link,
                "shop": "smart.md"
            }
            data.append(product)
        # for element in container:
        #     element.find_element(By.CLASS_NAME,'search-item search-product custom_product_content viewed')  # Adaugă conținutul HTML al elementului în listă
        #     print(element.text)
        # return data
        
    finally:
        driver.quit()  # Închide driver-ul browserului
    return data