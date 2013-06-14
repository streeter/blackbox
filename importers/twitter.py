#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Twitter importer.

Usage:
  twitter.py [--update] [--dry] [--pages=<p>]

Options:
  -h --help     Show this screen.
  -u --update   Update existing records.
  -d --dry      Executes a dry run.
  --pages=<p>   Number of pages to pull [default: 1].
"""

import json

from _util import *
from docopt import docopt

TIMELINE_URL = 'https://api.twitter.com/1.1/statuses/user_timeline.json'

def iter_tweets(exclude_replies=True, pages=1):

    params = {
        'exclude_replies': exclude_replies,
        'include_entities': True,
        'trim_user': True,
        'contributor_details': True,
        # 'max_id': '285391183943962624'
    }

    for page in range(pages):

        r = foauth.get(TIMELINE_URL, params=params)

        for tweet in r.json():
            yield tweet

        params['max_id'] = tweet['id']


def lookup_record(tweet):

    try:
        return blackbox.iter_search('metadata.service:twitter AND metadata.id:{}'.format(tweet['id'])).next()
    except Exception:
        return None


def main(update=False, dry=False, pages=1):
    for tweet in iter_tweets(pages=pages):
        existing = lookup_record(tweet)
        if existing:
            print 'Existing:',

            if not update:
                print '{0}. \nExiting.'.format(existing)
                return

        r = existing or blackbox.Record()
        r.epoch = epoch(parse(tweet[u'created_at']))
        r.content_type = 'application/json'
        r.ref = 'https://twitter.com/kennethreitz/status/{}'.format(tweet['id'])
        r.author = 'Kenneth Reitz'

        r.description = u'Tweet: {}'.format(tweet['text'])
        r.metadata['service'] = 'twitter'
        r.metadata['id'] = tweet['id']
        r.metadata['text'] = tweet['text']
        r.metadata['retweeted'] = tweet['retweeted']
        r.metadata['retweet_count'] = tweet['retweet_count']
        r.metadata['entities'] = tweet['entities']
        r.metadata['coordinates'] = tweet.get('coordinates')

        if not dry:
            r.save(archive=True)

            r.upload_task.delay(r, data=json.dumps(tweet), archive=True)
        print r







if __name__ == '__main__':
    arguments = docopt(__doc__, version='Twitter Importer')
    main(update=arguments['--update'], dry=arguments['--dry'], pages=int(arguments['--pages']))
