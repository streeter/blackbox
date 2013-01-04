#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""500px importer.

Usage:
  photos-500px.py [--update] [--dry]

Options:
  -h --help     Show this screen.
  -u --update   Update existing records.
  -d --dry      Executes a dry run.
"""


from _util import *
from docopt import docopt


username = foauth.get('https://api.500px.com/v1/users/').json()['user']['username']

def lookup_record(photo):

    try:
        return blackbox.iter_search('metadata.service:500px AND metadata.id:{}'.format(photo['id'])).next()
    except Exception:
        return None

def iter_photos():
    r = foauth.get('https://api.500px.com/v1/photos?feature=user&username={}'.format(username))
    total_pages = r.json()['total_pages']

    for i in range(total_pages):
        r = foauth.get('https://api.500px.com/v1/photos?feature=user&username={}&page={}'.format(username, i+1))
        for photo in r.json()['photos']:
            yield photo

def main(update=False, dry=False):
    for photo in iter_photos():

        existing = lookup_record(photo)
        if existing:
            print 'Existing:',

            if not update:
                print '{0}. \nExiting.'.format(existing)
                return

        r = existing or blackbox.Record()
        r.content_type = 'image/jpeg'
        r.ref = 'http://500px.com/photo/{}'.format(photo['id'])
        r.description = u'500px: {}, '.format(photo['name'], photo['description'])
        r.author = 'Kenneth Reitz'
        r.epoch = epoch(parse(photo[u'created_at']))

        r.metadata['service'] = '500px'
        r.metadata['height'] = photo['height']
        r.metadata['width'] = photo['width']
        r.metadata['id'] = photo['id']
        r.metadata['name'] = photo['name']
        r.metadata['description'] = photo['width']
        r.metadata['nsfw'] = photo['nsfw']
        r.metadata['src'] = photo['image_url'].replace('2.jpg', '4.jpg')

        if not dry:
            r.save(archive=True)

            r.upload_task.delay(r, url=photo['image_url'].replace('2.jpg', '4.jpg'), archive=True)
        print r

if __name__ == '__main__':
    arguments = docopt(__doc__, version='500px Importer')
    main(update=arguments['--update'], dry=arguments['--dry'])

