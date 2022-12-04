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
    region = request.args.get('region', 'wt-wt')
    safesearch = request.args.get('safesearch', 'Off')
    time = request.args.get('time', None)
    max_results = request.args.get('max_results', 3)

    if q:
        results = ddg(q, region=region, safesearch=safesearch, time=time, max_results=max_results, output=json)
        return results
    else:
        return 'Please provide a search query.'
