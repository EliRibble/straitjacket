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

import web
import json
import os
from lib import straitjacket

__author__ = "JT Olds"
__copyright__ = "Copyright 2011 Instructure, Inc."
__license__ = "AGPLv3"
__email__ = "jt@instructure.com"

DEFAULT_CONFIG_DIR = os.path.join(os.path.realpath(os.path.dirname(__file__)),
        "config")

INDEX_HTML = """
<h1>welcome to straitjacket</h1>
<form method="post" action="/execute">
<dl>
<dt>source:</dt><dd><textarea name="source" rows=8 cols=50></textarea></dd>
<dt>stdin:</dt><dd><textarea name="stdin" rows=8 cols=50></textarea></dd>
<dt>language:</dt><dd><select name="language">
%(languages)s
</select></dd></dl>
<input type="submit"/>
</form>
"""

class JSONWrapper(object):
    def __init__(self, json):
        self.json = json

    def __getattr__(self, name):
        try:
            return self.json[name]
        except KeyError:
            raise AttributeError

def webapp(wrapper=None, config_dir=DEFAULT_CONFIG_DIR, skip_language_checks=False):
    if not wrapper:
        wrapper = straitjacket.StraitJacket(config_dir, skip_language_checks=skip_language_checks)

    index_html = INDEX_HTML % {"languages": "\n".join(
            ('<option value="%s">%s - %s</option>' % (lang,
             wrapper.languages[lang].visible_name,
             wrapper.languages[lang].version)
             for lang in sorted(wrapper.languages.keys())))}

    class index:
        def GET(self):
            web.header('Content-Type', 'text/html')
            return index_html

    class execute:
        def POST(self):
            web.header('Content-Type', 'text/json')
            data = web.data()
            try:
                data = JSONWrapper(json.loads(data))
            except ValueError:
                data = web.input()

            timelimit = getattr(data, 'timelimit', None)
            timelimit = float(timelimit) if timelimit else None

            try:
                results = wrapper.run(data.language, data.source, data.stdin, custom_timelimit=timelimit)
                return json.dumps({
                        "stdout"                : results.stdout,
                        "stderr"                : results.stderr,
                        "returncode"            : results.returncode,
                        "time"                  : results.runtime,
                        "error"                 : results.error
                })
            except straitjacket.InputError:
                raise web.badrequest()
            except AttributeError:
                raise web.badrequest()

    class info:
        def GET(self):
            web.header('Content-Type', 'text/json')
            languages = {}
            for lang in wrapper.enabled_languages:
                languages[lang] = {
                        "visible_name": wrapper.enabled_languages[lang]["visible_name"],
                        "version": wrapper.enabled_languages[lang]["version"]}
            return json.dumps({"languages": languages})

    app = web.application((
            '/', 'index',
            '/execute', 'execute',
            '/info', 'info',
        ), locals())

    return app

if __name__ == "__main__":
        webapp().run()
application = webapp().wsgifunc()
