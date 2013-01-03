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

def main(update=False, dry=False):
    URL = 'http://api.flickr.com/services/rest/?method=flickr.people.getPhotos&user_id=me&per_page=500&format=json'

    r = foauth.get(URL)
    print r.content


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Flickr Importer')
    main(update=arguments['--update'], dry=arguments['--dry'])