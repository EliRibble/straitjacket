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

import time
import os
import subprocess
import threading
import base64
import shutil
import logging

try:
    import LibAppArmor
except ImportError:
    LibAppArmor = None

__author__ = "JT Olds"
__copyright__ = "Copyright 2011 Instructure, Inc."
__license__ = "AGPLv3"
__email__ = "jt@instructure.com"

class Error_(Exception): pass
class AppArmorProtectionFailure(Error_): pass

class ExecutionResults(object):
        def __init__(self, status, stdout, stderr, returncode, runtime):
                self.stdout         = stdout
                self.stderr         = stderr
                self.returncode = returncode
                self.runtime        = runtime
                self.status         = status

        def __repr__(self):
                return "Results returncode={0} {1} stdout={2} stderr={3}".format(self.returncode, 'error=' + self.error if self.error else '', self.stdout, self.stderr)

def aa_change_onexec(profile):
    if LibAppArmor is None or LibAppArmor.aa_change_onexec(profile) != 0:
        raise AppArmorProtectionFailure, ("failed to switch to apparmor profile %s"
                % profile)

class BaseProfile(object):

    def __init__(self, config):
        self.config = config

    def _kill(self, pid, completed, max_runtime=None):
        max_runtime = max_runtime if max_runtime else self.config.MAX_RUNTIME
        for _ in xrange(max(int(max_runtime), 1)):
            if completed: return
            time.sleep(1)
        if not completed:
            os.kill(pid, 9)
            completed.append("killed")

    def _run_user_program(self, user_program, stdin, aa_profile, time_used=0, executable=None, chdir=None, custom_timelimit=None):
        if custom_timelimit == None:
            custom_timelimit = float('inf')
        completed = []
        runtime = None
        start_time = time.time()

        def preexec_fn():
            if chdir: os.chdir(chdir)
            aa_change_onexec(aa_profile)

        proc = subprocess.Popen(user_program, executable=executable,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                close_fds=True, preexec_fn=preexec_fn)
        kill_thread = threading.Thread(target=self._kill, args=(proc.pid, completed,
                min(self.config.MAX_RUNTIME - time_used, custom_timelimit)))

        kill_thread.start()
        returncode = None
        try:
            stdout, stderr = proc.communicate(stdin)
        except Exception, e:
            stdout, stderr = "", str(e)
            returncode = None
        runtime = time.time() - start_time
        completed.append(True)
        kill_thread.join()

        if returncode is None:
            returncode = proc.returncode

        if "killed" in completed or runtime > custom_timelimit:
            status = "timeout"
        else:
            status = "success"

        return ExecutionResults(status, stdout, stderr, returncode, runtime)

    def _filename_gen(self): return base64.b64encode(os.urandom(42), "_-")

    def run(self, language, source, stdin, custom_timelimit=None):
        raise NotImplementedError


class CompilerProfile(BaseProfile):

    def __init__(self, config): BaseProfile.__init__(self, config)

    def run(self, language, source, stdin, custom_timelimit=None):
        source_dir = os.path.join(self.config.DIRECTORIES['source'], self._filename_gen())
        source_file = os.path.join(source_dir, language.filename)
        compiler_file = os.path.join(self.config.DIRECTORIES["compiler"], self._filename_gen())
        executable_file = os.path.join(self.config.DIRECTORIES["execution"], self._filename_gen())
        try:
            os.mkdir(source_dir)
            with open(source_file, 'w') as f:
                f.write(source)
            logging.debug("Wrote the following source to %s: %s", source_file, source)

            completed = []
            compile_start_time = time.time()
            logging.debug("Compiling with profile %s", language.apparmor_profile)
            def compiler_preexec():
                os.environ["TMPDIR"] = self.config.DIRECTORIES["compiler"]
                aa_change_onexec(language.apparmor_profile)

            if language.compilation_command:
                command = language.compilation_command(source_file, compiler_file)
            else:
                command = [language.binary, "-o", compiler_file, source_file]
            logging.debug("Executing command %s", command)
            proc = subprocess.Popen(command, stdin=None, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, close_fds=True, preexec_fn=compiler_preexec)
            kill_thread = threading.Thread(target=self._kill, args=(proc.pid,
                    completed))

            kill_thread.start()
            returncode = None
            try:
                compile_out = proc.communicate()[0]
            except Exception, e:
                compile_out = str(e)
                returncode = -9
            completed.append(True)
            kill_thread.join()

            if returncode is None: returncode = proc.returncode

            if returncode != 0:
                if "killed" in completed:
                    status = "compilation timeout"
                else:
                    status = "compilation failed"
                return ExecutionResults(status, "", compile_out, returncode, 0.0)

            os.rename(compiler_file, executable_file)

            if language.compiled_apparmor_profile:
                compiled_profile = language.compiled_apparmor_profile
            else:
                compiled_profile = self.config.APPARMOR_PROFILES["compiled"]

            return self._run_user_program(["straitjacket-binary"], stdin,
                    compiled_profile, time.time() - compile_start_time, executable_file,
                    custom_timelimit=custom_timelimit)
        finally:
            shutil.rmtree(source_dir)
            if os.path.exists(compiler_file): os.unlink(compiler_file)
            if os.path.exists(executable_file): os.unlink(executable_file)

    def default_apparmor_profile(self):
        return self.config.APPARMOR_PROFILES["compiler"]

class InterpreterProfile(BaseProfile):

    def __init__(self, config): BaseProfile.__init__(self, config)

    def run(self, language, source, stdin, custom_timelimit=None):
        dirname = os.path.join(self.config.DIRECTORIES["source"], self._filename_gen())
        filename = os.path.join(dirname, language.filename)
        os.makedirs(dirname)
        try:
            with open(filename, 'w') as f:
                f.write(source)
            if language.interpretation_command:
                command = language.interpretation_command(filename)
            else:
                command = [language.binary, filename]
            return self._run_user_program(command,
                         stdin,
                         language.apparmor_profile,
                         custom_timelimit=custom_timelimit)

        finally:
            shutil.rmtree(dirname)

    def default_apparmor_profile(self):
        return self.config.APPARMOR_PROFILES["interpreter"]


class VMProfile(BaseProfile):

    def __init__(self, config): BaseProfile.__init__(self, config)

    def run(self, language, source, stdin, custom_timelimit=None):
        source_dir = os.path.join(self.config.DIRECTORIES["source"],
                self._filename_gen())
        source_file = os.path.join(source_dir, language.filename)
        try:
            os.mkdir(source_dir)
            f = file(source_file, "w")
            try:
                f.write(source)
            finally:
                f.close()

            completed = []
            compile_start_time = time.time()

            logging.info("Switching to apparmor profile %s", language.compiler_apparmor_profile)
            def compiler_preexec():
                os.environ["TMPDIR"] = self.config.DIRECTORIES["compiler"]
                os.chdir(source_dir)
                aa_change_onexec(language.compiler_apparmor_profile)

            if language.compilation_command:
                command = language.compilation_command(source_file)
            else:
                command = [language.binary, source_file]
            logging.debug("Compiling with: %s", command)
            proc = subprocess.Popen(command, stdin=None, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, close_fds=True, preexec_fn=compiler_preexec)
            kill_thread = threading.Thread(target=self._kill, args=(proc.pid,
                    completed))

            kill_thread.start()
            returncode = None
            try:
                compile_out = proc.communicate()[0]
            except Exception, e:
                compile_out = str(e)
                returncode = -9
            completed.append(True)
            kill_thread.join()

            if returncode is None: returncode = proc.returncode

            if returncode != 0:
                if "killed" in completed:
                    status = "compilation timeout"
                else:
                    status = "compilation failed"
                return ExecutionResults(status, "", compile_out, returncode, 0.0)

            return self._run_user_program(language.vm_command(source_file),
                    stdin, language.vm_apparmor_profile,
                    time.time() - compile_start_time, chdir=source_dir,
                    custom_timelimit=custom_timelimit)
        finally:
            shutil.rmtree(source_dir)

    def default_apparmor_profile(self):
        return self.config.APPARMOR_PROFILES["compiled"]
