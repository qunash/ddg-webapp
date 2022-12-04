from flask import Flask
import requests
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
    keywords = request.args.get('keywords')
    region = request.args.get('region', 'wt-wt')
    safesearch = request.args.get('safesearch', 'Off')
    time = request.args.get('time', None)
    max_results = request.args.get('max_results', None)

    results = ddg(keywords, region=region, safesearch=safesearch, time=time, max_results=max_results)

    return jsonify(results)