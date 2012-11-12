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

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import logging
import pprint

from lib import straitjacket
import languages

LOGGER = logging.getLogger('server')

ROOT_DIRECTORY = os.path.realpath(os.path.dirname(__file__))
DEFAULT_CONFIG_DIR = os.path.join(ROOT_DIRECTORY, "config")

def _setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)-8s] %(process)-5d %(asctime)s %(name)s: %(message)s')
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)
    root.info("Set up logging")
_setup_logging()


def _get_file_content(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def main():
    if len(sys.argv) > 1:
        language = languages.get(sys.argv[1])
    else:
        language = languages.get('python')

    for test in language.tests:
        test.test()

if __name__ == "__main__":
    main()
