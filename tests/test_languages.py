#!/usr/bin/env python
#
# Copyright (C) 2011 Instructure, Inc.
#
# This file is part of StraitJacket.
#
# StraitJacket is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, version 3 of the License.
#
# StraitJacket is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
#
import os
import sys
sys.path.append( os.path.abspath( os.path.join( os.path.dirname( __file__ ), '..' ) ) )

import server
import unittest
import urllib
import json
import re

def _execute(webapp, params):
    return webapp.request('/execute', 'POST', urllib.urlencode(params))


def test_language_tests(language, test_number):
    assert language.tests[test_number].test()
    
    
