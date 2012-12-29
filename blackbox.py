# -*- coding: utf-8 -*-


import os
import json
import time
from datetime import datetime
from uuid import uuid4

from pyelasticsearch import ElasticSearch
from flask import Flask

app = Flask(__name__)

es = ElasticSearch(os.environ['ELASTICSEARCH'])


class Record(object):
    def __init__(self):
        self.uuid = str(uuid4())
        self.content_type = 'application/octet-stream'
        self.epoch = epoch()
        self.file_name = None
        self.ref = None
        self.links = {}
        self.metadata = {}

    @property
    def content(self):
        pass

    def save(self):
        pass

    def __repr__(self):
        return '<Record {0}>'.format(self.uuid)


def epoch(dt=None):
    if not dt:
        dt = datetime.utcnow()

    return time.mktime(dt.timetuple()) * 1000 + dt.microsecond / 1000


@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/search/')
def hello2():
    return 'Hello World!'

@app.route('/collections/', methods=['GET'])
def get_collection():
    return 'Hello World!'


@app.route('/collections/', methods=['POST'])
def post_collection():
    return 'Hello World!'


@app.route('/collections/', methods=['POST'])
def put_collection():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()