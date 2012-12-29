# -*- coding: utf-8 -*-

import os

from pyelasticsearch import ElasticSearch
from flask import Flask

app = Flask(__name__)

es = ElasticSearch(os.environ['ELASTICSEARCH'])


@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/search/')
def hello2():
    return 'Hello World!'

@app.route('/search/')
def hello3():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()