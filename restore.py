from blackbox import bucket, Record

from clint.textui import progress

def iter_metadata():
    for key in bucket.list():
        if key.name.endswith('.json'):
            yield key

print 'Indexing:'
for key in progress.bar([i for i in iter_metadata()]):
    r = Record.from_uuid(key.name[:-5])
    r.index()

print 'Done!'

