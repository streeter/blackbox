from requests import Session
import os
import sys

sys.path.insert(0, os.path.abspath('..'))
import blackbox
from dateutil.parser import parse
from blackbox import epoch

foauth = Session()
foauth.auth = (os.environ['FOAUTH_USER'], os.environ['FOAUTH_PASS'])

box = Session()
box.auth = (os.environ['SECRET_KEY'], os.environ['SECRET_KEY'])