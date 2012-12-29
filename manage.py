#!/usr/bin/env python

from flask.ext.script import Manager

from myapp import app

manager = Manager(app)

# TODO: purge elasticsearch
# TODO: seed elasticsearch

@manager.command
def hello():
    print "hello"

if __name__ == "__main__":
    manager.run()