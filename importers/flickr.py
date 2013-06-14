#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Flickr importer.

Usage:
  flickr.py [--update] [--dry]

Options:
  -h --help     Show this screen.
  -u --update   Update existing records.
  -d --dry      Executes a dry run.
"""



from _util import *
from docopt import docopt

URL = 'https://secure.flickr.com/services/rest/?method=flickr.people.getPhotos&user_id=me&per_page=100&format=json&nojsoncallback=1&extras=description,date_upload,date_taken,original_format,geo,path_alias,url_o'

def lookup_record(photo):

    try:
        return blackbox.iter_search('metadata.service:flickr AND metadata.id:{}'.format(photo['id'])).next()
    except Exception:
        return None


def iter_photos():

    r = foauth.get(URL)
    j = r.json()

    for page in range(j['photos']['pages']+1):
        r = foauth.get(URL, params={'page': page})
        j = r.json()
        for photo in j['photos']['photo']:
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
        r.ref = 'http://www.flickr.com/photos/{}/{}'.format(photo['pathalias'], photo['id'])
        r.description = u'Flickr photo. {}'.format(photo['title'])
        r.author = 'Chris Streeter'
        r.links['src'] = photo['url_o']
        r.epoch = int(photo[u'dateupload'])*1000

        r.metadata['id'] = photo['id']
        r.metadata['service'] = 'flickr'
        r.metadata['title'] = photo['title']
        r.metadata['taken'] = epoch(parse(photo[u'datetaken']))
        r.metadata['longitude'] = photo['longitude']
        r.metadata['latitude'] = photo['latitude']

        print r

        if not dry:
            r.save(archive=True)

            r.upload_task.delay(r, url=photo['url_o'], archive=True)



if __name__ == '__main__':
    arguments = docopt(__doc__, version='Flickr Importer')
    main(update=arguments['--update'], dry=arguments['--dry'])
