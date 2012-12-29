# -*- coding: utf-8 -*-


import os
import json
import time
from datetime import datetime
from uuid import uuid4

import requests
from boto.s3.connection import S3Connection
from celery import Celery
from flask import Flask, request, Response, jsonify
from pyelasticsearch import ElasticSearch

app = Flask(__name__)

# Statics.
ELASTICSEARCH_URL = os.environ['ELASTICSEARCH_URL']
S3_BUCKET = os.environ['S3_BUCKET']
S3_BUCKET_DOMAIN = os.environ.get('S3_BUCKET_DOMAIN')
CLOUDAMQP_URL = os.environ.get('CLOUDAMQP_URL')


# Connection pools.
es = ElasticSearch(ELASTICSEARCH_URL)
bucket = S3Connection().get_bucket(S3_BUCKET)
celery = Celery(broker=CLOUDAMQP_URL)


class Record(object):
    def __init__(self):
        self.uuid = str(uuid4())
        self.content_type = 'application/octet-stream'
        self.epoch = epoch()
        self.filename = None
        self.ref = None
        self.links = {}
        self.metadata = {}

    @classmethod
    def from_uuid(cls, uuid):
        key = bucket.get_key('{0}.json'.format(uuid))
        j = json.loads(key.read())['record']

        r = cls()
        r.uuid = j.get('uuid')
        r.content_type = j.get('content_type')
        r.epoch = j.get('epoch')
        r.filename = j.get('filename')
        r.ref = j.get('ref')
        r.links = j.get('links')
        r.metadata = j.get('metadata')

        return r

    def upload(self, data=None, url=None):
        key = bucket.new_key(self.uuid)

        if url:
            # TODO: upload files from external URL.
            r = requests.get(url)
            data = r.content

        if data:
            # TODO: Delay this to celery?.
            # No, just make the whole call outside of celery
            key.set_contents_from_string(data)
            key.make_public()

    @celery.task
    def upload_task(self, **kwargs):
        self.upload(**kwargs)

    @celery.task
    def index_task(self, **kwargs):
        self.index(**kwargs)

    @property
    def content(self):
        key = bucket.get_key(self.uuid)
        return key.read()

    @property
    def content_url(self):
        prefix = 'http://{}.s3.amazonaws.com'.format(S3_BUCKET)

        if S3_BUCKET_DOMAIN:
            prefix = 'http://{}'.format(S3_BUCKET_DOMAIN)

        return '{}/{}'.format(prefix, self.uuid)

    @property
    def archive_url(self):
        pass

    def save(self):
        self.persist()
        self.index()
        self.archive()

    def persist(self):
        key = bucket.new_key('{0}.json'.format(self.uuid))
        key.update_metadata({'Content-Type': 'application/json'})

        key.set_contents_from_string(self.json)


    def index(self):
         es.index("archives", "record", self.dict, id=self.uuid)

    def archive(self):
        pass

    @property
    def dict(self):
        return {
            'uuid': self.uuid,
            'content_type': self.content_type,
            'epoch': self.epoch,
            'filename': self.filename,
            'ref': self.ref,
            'links': self.links,
            'metadata': self.metadata
        }

    @property
    def json(self):
        return json.dumps({'record': self.dict})

    def __repr__(self):
        return '<Record {0}>'.format(self.uuid)


def epoch(dt=None):
    if not dt:
        dt = datetime.utcnow()

    return int(time.mktime(dt.timetuple()) * 1000 + dt.microsecond / 1000)


@app.route('/')
def hello():
    j = {
        'source': 'https://github.com/kennethreitz/blackbox',
        'curator': 'Kenneth Reitz',
        'resources': {
            '/records': 'The collection of records.',
            '/records/:id/content:': 'The content of the given record.',
            '/records/:id/ref': 'Redirects to reference URL.'
        }
    }
    return jsonify(blackbox=j)

@app.route('/filter')
def hello2():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()