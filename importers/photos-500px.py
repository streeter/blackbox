from _util import *


username = foauth.get('http://foauth.org/api.500px.com/v1/users/').json()['user']['username']


def iter_photos():
    r = foauth.get('http://foauth.org/api.500px.com/v1/photos?feature=user&username={}'.format(username))
    total_pages = r.json()['total_pages']

    for i in range(total_pages):
        r = foauth.get('http://foauth.org/api.500px.com/v1/photos?feature=user&username={}&page={}'.format(username, i+1))
        for photo in r.json()['photos']:
            yield photo


for photo in iter_photos():
    # print photo

    r = blackbox.Record()
    r.content_type = 'image/jpeg'
    r.ref = 'http://500px.com/photo/{}'.format(photo['id'])
    try:
        r.description = '500px: {}, '.format(photo['name'], photo['description'])
    except Exception, e:
        r.description = '500px photo'
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

    r.save()

    r.upload_task.delay(r, url=photo['image_url'].replace('2.jpg', '4.jpg'))
    print r