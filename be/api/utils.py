import re

def extract_numbers(price_str):
    return int(''.join(re.findall(r'\d+', price_str)))

def reformat_image(image):
    
    image = image.replace('.png', '.webp')
    image = image.replace('.jpg', '.webp')
    image = image.replace('.jpeg', '.webp')
    
    return image

data_numbers=5