#!/usr/bin/env python

from flask.ext.script import Manager
from clint.textui import progress
import importers
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
    print("hello")


@manager.command
def purge_index():
    es.delete_index('archives')

@manager.command
def seed_index():
    print('Indexing:')
    for key in progress.bar([i for i in iter_metadata()]):
        r = Record.from_uuid(key.name[:-5])
        r.index_task.delay(r)

@manager.command
def seed_archive():
    print('Archiving:')
    archive_keys = [key.name for key in archive.list()]

    for key in progress.bar([i for i in iter_metadata()]):
        if key.name not in archive_keys:
            r = Record.from_uuid(key.name[:-5])
            r.archive_task.delay(r)


@manager.command
def dupes():
    importers.dupes.main(dry=False)


@manager.command
def imports():
    dry = False
    update = False

    print('Importing Instagram')
    importers.instagram.main(dry=dry, update=update)

    print('Importing 500px')
    importers.photos500px.main(dry=dry, update=update)

    print('Importing Twitter')
    importers.twitter.main(dry=dry, update=update, pages=300)

    print('Importing Flickr')
    importers.flickr.main(dry=dry, update=update)


if __name__ == "__main__":
    manager.run()
