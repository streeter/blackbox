#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Archive importer.

Usage:
  archive.py <url> [--description=<t>] [--author=<a>]

Options:
  --description=<t>   Description of archive.
  --author=<a>        Author of archive.
"""

from _util import *
from docopt import docopt

def main(url, description=None, author='Chris Streeter'):

    if description is None:
        description = 'Archive of {}'.format(url)

        r = blackbox.Record()
        r.ref = url
        r.description = description
        r.author = author
        r.filename = url.split('/')[-1] or None

        r.metadata['archive'] = True

        r.save()
        r.upload_task.delay(r, url=url)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Archive Importer')
    args = {
        'url': arguments['<url>'],
        'description': arguments['--description'],
        'author': arguments['--author']
    }
    main(**args)
