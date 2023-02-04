from flask import Flask
from flask import request
from flask import jsonify
from duckduckgo_search import ddg
from newspaper import Article


app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

@app.route('/search')
def search():
    q = request.args.get('q')
    if not q:
        return error_response('Please provide a query.')

    try:
        region = request.args.get('region', 'wt-wt')
        safesearch = request.args.get('safesearch', 'Off')
        time = request.args.get('time', None)
        max_results = request.args.get('max_results', 3, type=int)
        max_results = min(max_results, 10)

        results = ddg(q, region=region, safesearch=safesearch, time=time, max_results=max_results)
        
        response = jsonify(results)

        return add_headers(response)

    except Exception as e:
        return error_response(f'Error searching: {e}')
    

@app.route('/url_to_text')
def url_to_text():
    url = request.args.get('url')
    if not url:
        return error_response('Please provide a URL.')
        
    try:
        title, text = extract_title_and_text_from_url(url)
    except Exception as e:
        return error_response(f'Error extracting text from URL: {e}')

    response = jsonify([{
        'body': text,
        'href': url,
        'title': title
    }])

    return add_headers(response)

def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'https://chat.openai.com'
    return response

def error_response(message):
    response = jsonify([{
        'body': message,
        'href': '',
        'title': ''
    }])
    
    return add_headers(response)

def extract_title_and_text_from_url(url: str):

    article = Article(url)
    article.download()
    article.parse()
    
    return article.title, article.text