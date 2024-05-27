# from flask import Flask, request, jsonify
# import requests
# from bs4 import BeautifulSoup
# from concurrent.futures import ThreadPoolExecutor
# from flask_cors import CORS
# from parsers.parse_darwin import parse_darwin
# from parsers.parse_smart_md import parse_smart_md
# from parsers.parse_istore_md import parse_istore_md
# from parsers.parse_maximum_md import parse_maximum_md

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})


# store_parsers = {
#     'darwin': {
#         'url': 'https://94.158.246.177/search?search=',
#         'parser': parse_darwin
#     },
#     'smart_md': {
#         'url': 'https://www.smart.md/s?query=',
#         'parser': parse_smart_md
#     },
#     'istore_md': {
#         'url': 'https://istore.md/cautare?keywords=',
#         'parser': parse_istore_md
#     },
#     'maximum_md': {
#         'url': 'https://maximum.md/ro/search?query=',
#         'parser': parse_maximum_md
#     }
# }


# @app.route('/')
# def home():
#     print("Hello")
#     return "Welcome to the Flask Parsing Server!"

# @app.route('/parse_all', methods=['POST'])
# def get_all_data():
#     search = request.json.get('search')
#     page = request.json.get('page', 1)  
#     # search += "&page=" + str(page)
    
 
#     aggregated_results = []

#     for store, parser_data in store_parsers.items():
#         url = parser_data['url'] + search
#         parsed_data = parser_data['parser'](url)
#         aggregated_results.extend(parsed_data)

#     aggregated_results = get_filtered_projects('Scumpe', list(aggregated_results))

#     return aggregated_results
#     # return parsed_data/





  
# @app.route('/get', methods=['POST'])
# def get_html():
#     data = request.get_json()
#     url = data.get('url')
#     if not url:
#         return jsonify({'error': 'URL not provided'}), 400

#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         return response.text
#     except requests.exceptions.RequestException as e:
#         return jsonify({'error': str(e)}), 500



# @app.route('/filter', methods=['POST'])
# def get_filtered_projects(filter_value=None, data=None):
#     if data is None and filter_value is None:
#         data = request.json.get('data')
#         filter_value = request.json.get('filter')

#     if filter_value == 'Ieftine':
#         data.sort(key=lambda x: x.get('price', 0))
#     if filter_value == 'Scumpe':
#         data.sort(key=lambda x: x.get('price', 0), reverse=True)
#     if filter_value == 'Reduceri':
#         data.sort(key=lambda x: x.get('discount', 0), reverse=True)

#     return jsonify(data)


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from parsers.parse_darwin import parse_darwin
from parsers.parse_smart_md import parse_smart_md
from parsers.parse_istore_md import parse_istore_md
from parsers.parse_maximum_md import parse_maximum_md

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

store_parsers = {
    'darwin': {
        'url': 'https://94.158.246.177/search?search=',
        'parser': parse_darwin
    },
    'smart_md': {
        'url': 'https://www.smart.md/s?query=',
        'parser': parse_smart_md
    },
    'istore_md': {
        'url': 'https://istore.md/cautare?keywords=',
        'parser': parse_istore_md
    },
    'maximum_md': {
        'url': 'https://maximum.md/ro/search?query=',
        'parser': parse_maximum_md
    }
}

@app.route('/')
def home():
    return "Welcome to the Flask Parsing Server!"

@app.route('/parse_all', methods=['POST'])
def get_all_data():
    search = request.json.get('search')
    page = request.json.get('page', 1)

    aggregated_results = []
    total_stores = len(store_parsers)
    parsed_count = 0

    for store, parser_data in store_parsers.items():
        url = parser_data['url'] + search
        parsed_data = parser_data['parser'](url)
        aggregated_results.extend(parsed_data)
        parsed_count += 1
        progress = parsed_count/total_stores
        socketio.emit('progress', {'progress': progress})

    aggregated_results = get_filtered_projects('Scumpe', list(aggregated_results))

    return aggregated_results


  
@app.route('/get', methods=['POST'])
def get_html():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL not provided'}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500



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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
