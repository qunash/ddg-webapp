import re
from flask import Flask, request, jsonify, Response
from duckduckgo_search import ddg
from newspaper import Article
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://chat.openai.com"}})

@app.route('/')
def home():
    return 'Wow, it works!'

@app.route('/search')
def search():
    user_agent = request.headers.get('User-Agent', '').lower()
    if 'axios' in user_agent:
        return jsonify({})

    q = request.args.get('q')
    if not q:
        return error_response('Please provide a query.')

    try:
        q = q[:500]
        q = escape_ddg_bangs(q)
        region = request.args.get('region', 'wt-wt')
        safesearch = request.args.get('safesearch', 'Off')
        time = request.args.get('time', None)
        max_results = request.args.get('max_results', 3, type=int)
        max_results = min(max_results, 10)

        results = ddg(q, region=region, safesearch=safesearch, time=time, max_results=max_results)
        response = jsonify(results)
        return response

    except Exception as e:
        return error_response(f'Error searching: {e}')

def escape_ddg_bangs(q):
    q = re.sub(r'^!', r'', q)
    q = re.sub(r'\s!', r' ', q)
    return q

@app.route('/url_to_text')
def url_to_text():
    user_agent = request.headers.get('User-Agent', '').lower()
    if 'axios' in user_agent:
        return jsonify({})

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

    return response

def error_response(message):
    response = jsonify([{
        'body': message,
        'href': '',
        'title': ''
    }])
    
    return response

def extract_title_and_text_from_url(url: str):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url

    article = Article(url)
    article.download()
    article.parse()

    return article.title, article.text

if __name__ == '__main__':
    app.run(debug=True)

