# -*- coding: utf-8 -*-


import os
import json
import time
from datetime import datetime
from uuid import uuid4

import redis
import requests
import boto
from boto.s3.connection import S3Connection
from celery import Celery
from flask import Flask, request, Response, jsonify, redirect, url_for
from werkzeug.contrib.cache import RedisCache
from pyelasticsearch import ElasticSearch
from flask.ext.cache import Cache

app = Flask(__name__)
app.debug = os.environ.get('DEBUG')

# Statics.
ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', os.environ.get('BONSAI_URL'))
S3_BUCKET = os.environ['S3_BUCKET']
S3_BUCKET_DOMAIN = os.environ.get('S3_BUCKET_DOMAIN')
CLOUDAMQP_URL = os.environ.get('CLOUDAMQP_URL')
REDIS_URL = os.environ.get('OPENREDIS_URL', os.environ.get('REDISTOGO_URL'))
IA_ACCESS_KEY_ID = os.environ.get('IA_ACCESS_KEY_ID')
IA_SECRET_ACCESS_KEY = os.environ.get('IA_SECRET_ACCESS_KEY')
IA_BUCKET = os.environ.get('IA_BUCKET')
SEARCH_TIMEOUT = 50

# Connection pools.
celery = Celery(broker=CLOUDAMQP_URL)
es = ElasticSearch(ELASTICSEARCH_URL)
bucket = S3Connection().get_bucket(S3_BUCKET)
ia = boto.connect_ia(IA_ACCESS_KEY_ID, IA_SECRET_ACCESS_KEY)
archive = ia.lookup(IA_BUCKET)

cache = Cache()
cache.cache = RedisCache()
cache.cache._client = redis.from_url(REDIS_URL)

class Record(object):
    def __init__(self):
        self.uuid = str(uuid4())
        self.content_type = 'application/octet-stream'
        self.epoch = epoch()
        self.added = epoch()
        self.filename = None
        self.ref = None
        self.description = None
        self.author = None
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
        r.added = j.get('added')
        r.filename = j.get('filename')
        r.ref = j.get('ref')
        r.links = j.get('links')
        r.metadata = j.get('metadata')
        r.description = j.get('description')
        r.author = j.get('author')

        return r

    @classmethod
    def from_hit(cls, hit):
        j = hit['_source']

        r = cls()
        r.uuid = j.get('uuid')
        r.content_type = j.get('content_type')
        r.epoch = j.get('epoch')
        r.added = j.get('added')
        r.filename = j.get('filename')
        r.ref = j.get('ref')
        r.links = j.get('links')
        r.metadata = j.get('metadata')
        r.description = j.get('description')
        r.author = j.get('author')

        return r

    def upload(self, data=None, url=None, archive=False):

        if url:
            r = requests.get(url)
            data = r.content

        if data:
            key = bucket.new_key(self.uuid)

            if self.content_type:
                key.update_metadata({'Content-Type': self.content_type})

            key.set_contents_from_string(data)
            key.make_public()

        if archive:
            self.archive_upload(data=data, url=url)

    @celery.task
    def upload_task(self, **kwargs):
        self.upload(**kwargs)

    @celery.task
    def index_task(self, **kwargs):
        self.index(**kwargs)

    @celery.task(rate_limit='30/m')
    def archive_task(self, **kwargs):
        self.archive(**kwargs)

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
    def meta_url(self):
        return '{}.json'.format(self.content_url)

    @property
    def content_archive(self):
        return 'http://archive.org/download/{}/{}'.format(IA_BUCKET, self.uuid)

    @property
    def meta_archive(self):
        return '{}.json'.format(self.content_archive)

    def save(self, archive=False):

        self.persist()
        self.index()

        if False and archive:
            self.archive(upload=False)

    def persist(self):
        key = bucket.new_key('{0}.json'.format(self.uuid))
        key.update_metadata({'Content-Type': 'application/json'})

        key.set_contents_from_string(self.json)
        key.make_public()


    def index(self):
         es.index("archives", "record", self.dict, id=self.uuid)

    def archive(self, upload=False):

        key_name = '{0}.json'.format(self.uuid)

        key = archive.new_key(key_name)
        key.update_metadata({'Content-Type': 'application/json'})

        key.set_contents_from_string(self.json)

        if upload:
            self.archive_upload(url=self.content_url)

    def archive_upload(self, data=None, url=None):
        if url:
            r = requests.get(url)
            data = r.content

        if data:
            key = archive.new_key(self.uuid)

            if self.content_type:
                key.update_metadata({'Content-Type': self.content_type})

            key.set_contents_from_string(data)

    @property
    def dict(self):
        return {
            'uuid': self.uuid,
            'content_type': self.content_type,
            'epoch': self.epoch,
            'added': self.added,
            'filename': self.filename,
            'ref': self.ref,
            'links': self.links,
            'metadata': self.metadata,
            'description': self.description,
            'author': self.author
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

def iter_search(query, **kwargs):

    if query is None:
        query = '*'
    # Pepare elastic search queries.
    params = {}
    for (k, v) in kwargs.items():
        params['es_{0}'.format(k)] = v

    params['es_q'] = query

    q = {
        'sort': [
            {"epoch" : {"order" : "desc"}},
        ]
    }

    # if query:
    q['query'] = {'term': {'query': query}},


    results = es.search(q, index='archives', **params)
    # print results

    params['es_q'] = query
    for hit in results['hits']['hits']:
        yield Record.from_hit(hit)

@cache.memoize(timeout=SEARCH_TIMEOUT)
def search(query, sort=None, size=None, **kwargs):
    if sort is not None:
        kwargs['sort'] = sort
    if size is not None:
        kwargs['size'] = size

    return [r for r in iter_search(query, **kwargs)]

@app.route('/')
def hello():
    j = {
        'source': 'https://github.com/kennethreitz/blackbox',
        'curator': 'Kenneth Reitz',
        'resources': {
            '/records': 'The collection of records.',
            '/records/:id': 'The metadata of the given record.',
            '/records/:id/download': 'The content of the given record.',
        }
    }
    return jsonify(blackbox=j)

@app.route('/records/')
def get_records():

    args = request.args.to_dict()
    results = search(request.args.get('q'), **args)

    def gen():
        for result in results:
            d = result.dict
            d['links']['path:meta'] = result.meta_url
            d['links']['path:data'] = result.content_url
            d['links']['archive:meta'] = result.meta_archive
            d['links']['archive:data'] = result.content_archive

            yield d

    return jsonify(records=[r for r in gen()])

@app.route('/records/<uuid>')
def get_record(uuid):
    r = Record.from_uuid(uuid)
    return jsonify(record=r.dict)

@app.route('/records/<uuid>/download')
def download_record(uuid):
    r = Record.from_uuid(uuid)
    return redirect(r.content_url)



if __name__ == '__main__':
    app.run()
