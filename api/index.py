from flask import Flask
from flask import request
from flask import jsonify
from duckduckgo_search import ddg


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
        response = jsonify([{
            'body': 'Please provide a search query.',
            'href': '',
            'title': ''
        }])
        response.headers['Access-Control-Allow-Origin'] = 'https://chat.openai.com'
        return response

    region = request.args.get('region', 'wt-wt')
    safesearch = request.args.get('safesearch', 'Off')
    time = request.args.get('time', None)
    max_results = request.args.get('max_results', 3, type=int)
    max_results = min(max_results, 10)

    results = ddg(q, region=region, safesearch=safesearch, time=time, max_results=max_results)

    response = jsonify(results)
    response.headers['Access-Control-Allow-Origin'] = 'https://chat.openai.com' # This is necessary to allow requests from the chrome extension on https://chat.openai.com
    return response
