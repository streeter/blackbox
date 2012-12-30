# -*- coding: utf-8 -*-

"""This module contains shares utilities that are used for all importers."""

import os
import sys

from requests import Session
from requests_foauth import Foauth

sys.path.insert(0, os.path.abspath('..'))
import blackbox
from dateutil.parser import parse
from blackbox import epoch

foauth = Session()
foauth.mount('http', Foauth(os.environ['FOAUTH_USER'], os.environ['FOAUTH_PASS']))

# box = Session()
# box.auth = (os.environ['SECRET_KEY'], os.environ['SECRET_KEY'])