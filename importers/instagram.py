#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Instagram importer.

Usage:
  instagram.py [--update]

Options:
  -h --help     Show this screen.
  -u --update   Update existing records.
"""



from _util import *
from docopt import docopt


URL = 'https://foauth.org/api.instagram.com/v1/users/self/media/recent'

def lookup_record(photo):

    try:
        return blackbox.iter_search('metadata.service:instagram AND metadata.id:{}'.format(photo['id'])).next()
    except Exception:
        return None

def iter_pages():
    r = foauth.get(URL)

    yield r.json()

    next = r.json()['pagination'].get('next_max_id')

    while next:
        r = foauth.get(URL, params={'max_id': next})

        yield r.json()

        next = r.json()['pagination'].get('next_max_id')


def iter_photos():

    for page in iter_pages():
        for i in page['data']:

            j = {
                'id': i['id'],
                'url': i['images']['standard_resolution']['url'],
                'link': i['link'],
                'location': i.get('location'),
                'filter': i['filter'],
                'caption': i['caption']['text'] if i.get('caption') else None,
                'created': int(i['created_time'])
            }

            yield j


def main(update=False):
    for photo in iter_photos():

        existing = lookup_record(photo)
        print 'Existing:',
        if existing and not update:
            print '{} found, exiting.'.format(existing)
            exit()

        r = existing or blackbox.Record()

        r.content_type = 'image/jpeg'
        r.ref = photo['link']
        r.description = 'Instagram by @kennethreitz. Caption: {}'.format(photo['caption'])
        r.author = 'Kenneth Reitz'
        r.links['src'] = photo['url']
        r.epoch = photo['created'] * 1000

        r.metadata['id'] = photo['id']
        r.metadata['service'] = 'instagram'
        r.metadata['filter'] = photo['filter']
        r.metadata['location'] = photo['location']
        r.metadata['caption'] = photo['caption']

        r.save()

        r.upload_task.delay(r, url=photo['url'])
        print r



if __name__ == '__main__':
    arguments = docopt(__doc__, version='Instagram Importer')
    main(arguments['--update'])
