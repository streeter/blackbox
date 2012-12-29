#!/usr/bin/env python

from flask.ext.script import Manager
from clint.textui import progress

from blackbox import *

def iter_metadata():
    for key in bucket.list():
        if key.name.endswith('.json'):
            yield key


manager = Manager(app)

# TODO: purge elasticsearch
# TODO: seed elasticsearch

@manager.command
def hello():
    print "hello"


@manager.command
def purge_index():
    es.delete_index('archives')

@manager.command
def seed_index():
    print 'Indexing:'
    for key in progress.bar([i for i in iter_metadata()]):
        r = Record.from_uuid(key.name[:-5])
        r.index()


if __name__ == "__main__":
    manager.run()