import re

def extract_numbers(price_str):
    return int(''.join(re.findall(r'\d+', price_str)))