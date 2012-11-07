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

import languages
from errors import InputError

REQUIRED_TESTS = ["test-simple", "test-rlimit", "test-apparmor"]
def stderr_log(msg):
    print >> sys.stderr, msg

class StraitJacket(object):

    def __init__(self, config_dir, log_method=None, skip_language_checks=False):
        self.log_method = log_method or stderr_log

        self.languages = {language.name: language for language in languages.all()}

        if not skip_language_checks:
            self.log_method("Initialized %d languages" % (
                    len(self.languages)))

    def run(self, language, source, stdin, custom_timelimit=None):
        try:
            return self.languages[language].execute(source, stdin, custom_timelimit)
        except KeyError as k:
            raise InputError, "invalid language"

