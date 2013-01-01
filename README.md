Blackbox
========

This is an experimental publishing platform that represents a culmination of  many of my passions and values: APIs, simplicity, persistence, and nostalgia.

Everything I ever publish will have:

- Permanent URLs
- Query & Search
- Continual Replication

Example Queries
---------------

- [any containing heroku](http://blackbox.kennethreitz.org/records/?q=heroku)
- [photos in paris](http://blackbox.kennethreitz.org/records/?q=metadata.service:500px%20AND%20paris%20in%20description)
- [instagrams in reverse order](http://blackbox.kennethreitz.org/records/?q=metadata.service:instagram&sort=epoch:asc)
- [instagrams with X-Pro II filter](http://blackbox.kennethreitz.org/records/?q=metadata.service:instagram%20AND%20metadata.filter:X-Pro%20II)

Everything is backed up and replicated. If every social network shuts down net week, I can instantly see any [tweet](http://archive.kennethreitz.org/42b7e752-df3e-46ae-a80e-95c2663d8895) or [photo](http://blackbox.kennethreitz.org/records/2b0ee27e-ce90-48cb-8fb8-c2cd782be990/download) I've ever published.

This is the opposite of the [410 GONE](http://www.economist.com/blogs/babbage/2011/10/internet-culture) situation.