# -*- coding: utf-8 -*-


import os
import json
import time
from datetime import datetime
from uuid import uuid4

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from pyelasticsearch import ElasticSearch
from flask import Flask

app = Flask(__name__)

es = ElasticSearch(os.environ['ELASTICSEARCH_URL'])
bucket = S3Connection().create_bucket(os.environ['S3_BUCKET'])

class Record(object):
    def __init__(self):
        self.uuid = str(uuid4())
        self.content_type = 'application/octet-stream'
        self.epoch = epoch()
        self.filename = None
        self.ref = None
        self.links = {}
        self.metadata = {}

    @property
    def content(self):
        pass

    def save(self):
        self.persist()
        self.index()
        self.archive()

    def persist(self):
        key = bucket.lookup('{0}.json'.format(self.uuid))
        key.update_metadata({'Content-Type': 'application/json'})

        key.set_contents_from_string(self.json())

    def index(self):
        pass

    def archive(self):
        pass

    def json(self):
        return json.dumps({
            'uuid': self.uuid,
            'content_type': self.content_type,
            'epoch': self.epoch,
            'filename': self.filename,
            'ref': self.ref,
            'links': self.links,
            'metadata': self.metadata
        })

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