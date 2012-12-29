import requests
from blackbox import Record


r = Record()
r.metadata['test'] = True
r.metadata['life'] = 42
r.ref = 'http://en.wikipedia.org/wiki/Douglas_Adams'
r.upload.delay(r, data=requests.get(r.ref).content)
r.save()