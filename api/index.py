import re
from flask import Flask
from flask import request
from flask import jsonify
from duckduckgo_search import ddg
from newspaper import Article


app = Flask(__name__)

@app.route('/envir')
def envir():
    return str(request)


@app.route('/')
def home():
    return 'Wow, it works!'

@app.route('/about')
def about():
    return 'About'


def allowed_origin(request):
    origin = request.headers.get('Origin')
    return origin and origin.startswith('https://chat.openai.com')

@app.route('/search')
def search():

    if not request.referrer or not request.referrer.startswith('https://chat.openai.com'):
        return 'Access Denied', 403
    # if not allowed_origin(request):
    #     return 'Access Denied', 403

    q = request.args.get('q')
    if not q:
        return error_response('Please provide a query.')

    try:
        q = escape_ddg_bangs(q)
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

def escape_ddg_bangs(q):
    q = re.sub(r'^!', r'', q)
    q = re.sub(r'\s!', r' ', q)
    return q

@app.route('/url_to_text')
def url_to_text():
    
    # if not request.referrer or not request.referrer.startswith('https://chat.openai.com'):
    #     return 'Access Denied', 403
    # if not allowed_origin(request):
        # return 'Access Denied', 403
    response = jsonify([{
        'request.environ.get("HTTP_REFERER", "default value")': request.environ.get('HTTP_REFERER', 'default value'),
        'request.environ.get("HTTP_ORIGIN", "default value")': request.environ.get('HTTP_ORIGIN', 'default value'),
        'request.headers.get("Origin")': request.headers.get('Origin'),
        'request.referrer': request.referrer
    }])
    return add_headers(response)

    url = request.args.get('url')
    if not url:
        return error_response('Please provide a URL.')

    if '.' not in url:
        return error_response('Invalid URL.')
        
    try:
        title, text = extract_title_and_text_from_url(url)
    except Exception as e:
        return error_response(f'Error extracting text from URL: {e}')

    text = re.sub(r'\n{4,}', '\n\n\n', text)

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

    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url

    article = Article(url)
    article.download()
    article.parse()
    
    return article.title, article.text
