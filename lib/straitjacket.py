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
import logging
import languages
from errors import InputError

REQUIRED_TESTS = ["test-simple", "test-rlimit", "test-apparmor"]

class StraitJacket(object):

    def __init__(self, skip_language_checks=True):
        self.languages = {language.name: language for language in languages.all()}

        if not skip_language_checks:
            logging.debug("Initialized %d languages", len(self.languages))

    def run(self, language, source, stdin, timelimit=30):
        try:
            return self.languages[language].execute(source, stdin, timelimit)
        except KeyError:
            raise InputError, "invalid language"

