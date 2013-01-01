#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Dupes Remover.

Usage:
  dupes.py [--dry]

Options:
  -h --help     Show this screen.
  -d --dry      Executes a dry run.
"""

import json
from _util import *
from docopt import docopt
from clint.textui import progress

# {service: {service-key: [keys]}}

db = {
    'instagram': {},
    'twitter': {}
}
dupes = set()
contentless = set()

service_keys = {
    'instagram': 'id',
    'twitter': 'id'
}

def sort_dupes(j):

    service = j['metadata'].get('service')

    if service in service_keys:
        ident_k = service_keys[service]
        ident = j['metadata'][ident_k]
        uuid = j['uuid']

        if db[service].get(ident) is None:
            db[service][ident] = []
        else:
            dupes.add(uuid)

        db[service][ident].append(uuid)


def has_content(uuid):
    # logger.info('Checking content of {}'.format(uuid))
    return uuid in blackbox.bucket

def remove(uuid, dry=False):
    print 'removing', uuid
    if not dry:
        try:
            blackbox.es.delete('archives', 'record', uuid)
        except Exception:
            pass
        try:
            blackbox.bucket.delete_key('{}.json'.format(uuid))
        except Exception:
            pass
        try:
            blackbox.bucket.delete_key(uuid)
        except Exception:
            pass


def iter_metadata():
    for key in blackbox.bucket:
        if key.name.endswith('.json'):
            yield key

def main(dry=False):
    print 'Iterating over keys...'

    for key in progress.bar(list(iter_metadata())):
        j = json.loads(key.get_contents_as_string())['record']

        uuid = j['uuid']

        if not has_content(uuid):
            contentless.add(uuid)
        else:
            sort_dupes(j)

    print 'Deleting {} contentless found...'.format(len(contentless))
    for k in list(contentless):
        remove(k, dry=dry)

    print 'Deleting {} dupes found...'.format(len(dupes))
    for dupe in dupes:
        remove(dupe, dry=dry)




if __name__ == '__main__':
    arguments = docopt(__doc__, version='Dupes Remover')
    main(dry=arguments['--dry'])