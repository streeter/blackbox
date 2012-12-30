from _util import *

URL = 'https://foauth.org/api.instagram.com/v1/users/self/media/recent'

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
                'url': i['images']['standard_resolution']['url'],
                'link': i['link'],
                'location': i.get('location'),
                'filter': i['filter'],
                'caption': i['caption']['text'] if i.get('caption') else None,
                'created': int(i['created_time'])
            }

            yield j


for photo in iter_photos():
    print photo,

    r = blackbox.Record()
    r.content_type = 'image/jpeg'
    r.ref = photo['link']
    r.description = 'Instagram by @kennethreitz. Caption: {}'.format(photo['caption'])
    r.author = 'Kenneth Reitz'
    r.links['src'] = photo['url']
    r.epoch = photo['created'] * 1000

    r.metadata['service'] = 'instagram'
    r.metadata['instagram_filter'] = photo['filter']
    r.metadata['location'] = photo['location']
    r.metadata['caption'] = photo['caption']

    r.save()

    r.upload_task.delay(r, url=photo['url'])
    print r

