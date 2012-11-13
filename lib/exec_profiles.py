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

from errors import AppArmorProtectionFailure
from timeout import ProcessTimeout

try:
    import LibAppArmor
except ImportError:
    LibAppArmor = None

LOGGER = logging.getLogger('execution profiles')

__author__ = "JT Olds"
__copyright__ = "Copyright 2011 Instructure, Inc."
__license__ = "AGPLv3"
__email__ = "jt@instructure.com"

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
            if completed:
                return
            time.sleep(1)
        if not completed:
            os.kill(pid, 9)
            completed.append("killed")

    def _run_user_program(self, user_program, stdin, aa_profile, time_used=0, executable=None, chdir=None, timelimit=30, source_file=None):
        runtime = None
        start_time = time.time()

        def preexec_fn():
            if chdir:
                os.chdir(chdir)
            aa_change_onexec(aa_profile)

        proc = subprocess.Popen(user_program,
                                executable=executable,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                close_fds=True,
                                preexec_fn=preexec_fn)

        timeout = min(self.config.MAX_RUNTIME - time_used, timelimit)
        timer = ProcessTimeout(timeout, proc.pid)
        with timer:
            stdout, stderr = proc.communicate(stdin)
        returncode = proc.wait()

        runtime = time.time() - start_time

        if timer.timedout:
            status = 'timeout'
            returncode = None
        else:
            status = "success"

        # Clean out any incriminating information about our file system
        if source_file:
            stdout = stdout.replace(source_file, '<source>')
            stderr = stderr.replace(source_file, '<source>')

        return {
            'status'        : status,
            'stdout'        : stdout,
            'stderr'        : stderr,
            'returncode'    : returncode,
            'runtime'       : runtime
        }

    def _filename_gen(self):
        return base64.b64encode(os.urandom(42), "_-")

    def run(self, language, source, stdin, timelimit=30):
        raise NotImplementedError


class CompilerProfile(BaseProfile):

    def __init__(self, config):
        BaseProfile.__init__(self, config)

    def run(self, language, source, stdins, timelimit=30):
        compile_start_time = time.time()
        stdins = [stdins] if isinstance(stdins, basestring) or stdins is None else stdins
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
            compile_out, compile_err = proc.communicate()
            completed.append(True)
            kill_thread.join()

            compilation_time = time.time() - compile_start_time
        
            compile_out = compile_out.replace(source_file, '<source>') if compile_out else ''
            compile_err = compile_err.replace(source_file, '<source>') if compile_err else ''
            
            compile_out = compile_out.replace(self.config.DIRECTORIES['compiler'], '<tmp_dir>')
            compile_err = compile_err.replace(self.config.DIRECTORIES['compiler'], '<tmp_dir>')

            results = {
                'compilation'       : {
                    'command'           : ' '.join(command).replace(compiler_file, '<output>').replace(source_file, '<source>'),
                    'stdout'            : compile_out,
                    'stderr'            : compile_err,
                    'returncode'        : proc.returncode,
                    'time'              : compilation_time
                }
            }

            if proc.returncode != 0:
                results['status'] = 'compilation timeout' if 'killed' in completed else 'compilation failed'
                results['runs'] = []
                return results

            os.rename(compiler_file, executable_file)

            if language.compiled_apparmor_profile:
                compiled_profile = language.compiled_apparmor_profile
            else:
                compiled_profile = self.config.APPARMOR_PROFILES["compiled"]

            time_left = timelimit - compilation_time
            per_run_timelimit = time_left / len(stdins)

            run_results = [self._run_user_program(["straitjacket-binary"],
                            stdin,
                            compiled_profile,
                            compilation_time,
                            executable_file,
                            timelimit=per_run_timelimit) for stdin in stdins]
            results['runs'] = run_results
            results['status'] = 'success'
            return results

        finally:
            shutil.rmtree(source_dir)
            if os.path.exists(compiler_file):
                os.unlink(compiler_file)
            if os.path.exists(executable_file):
                os.unlink(executable_file)

    def default_apparmor_profile(self):
        return self.config.APPARMOR_PROFILES["compiler"]

class InterpreterProfile(BaseProfile):

    def __init__(self, config):
        BaseProfile.__init__(self, config)

    def run(self, language, source, stdins, timelimit=30):
        stdins = [stdins] if isinstance(stdins, basestring) or stdins is None else stdins

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
            per_run_timelimit = timelimit / len(stdins)
            return {
                'status'    : 'success',
                'runs'      : [self._run_user_program(command,
                                stdin,
                                language.apparmor_profile,
                                timelimit=per_run_timelimit,
                                source_file=filename) for stdin in stdins]
            }

        finally:
            shutil.rmtree(dirname)

    def default_apparmor_profile(self):
        return self.config.APPARMOR_PROFILES["interpreter"]


class VMProfile(BaseProfile):

    def __init__(self, config):
        BaseProfile.__init__(self, config)

    def run(self, language, source, stdins, timelimit=30):
        compile_start_time = time.time()
        stdins = [stdins] if isinstance(stdins, basestring) or stdins is None else stdins
        source_dir = os.path.join(self.config.DIRECTORIES["source"], self._filename_gen())
        source_file = os.path.join(source_dir, language.filename)
        try:
            os.mkdir(source_dir)
            f = file(source_file, "w")
            try:
                f.write(source)
            finally:
                f.close()

            completed = []

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
            proc = subprocess.Popen(command, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True, preexec_fn=compiler_preexec)
            kill_thread = threading.Thread(target=self._kill, args=(proc.pid, completed, language.compiler_timeout))

            kill_thread.start()
            compile_out, compile_err = proc.communicate()
            completed.append(True)
            kill_thread.join()

            compilation_time = time.time() - compile_start_time
            results = {
                'compilation'       : {
                    'command'           : ' '.join(command).replace(source_file, '<source>'),
                    'stdout'            : compile_out.replace(source_file, '<source>') if compile_out else '',
                    'stderr'            : compile_err.replace(source_file, '<source>') if compile_err else '',
                    'returncode'        : proc.returncode,
                    'time'              : compilation_time
                },
                'runs'              : []
            }

            if proc.returncode != 0:
                results['status'] = 'compilation timeout' if 'killed' in completed else 'compilation failed'
                return results

         
            time_left = timelimit - compilation_time
            per_run_timelimit = time_left / len(stdins)   
            run_results = [self._run_user_program(language.vm_command(source_file),
                                stdin,
                                language.vm_apparmor_profile,
                                compilation_time,
                                chdir=source_dir,
                                timelimit=per_run_timelimit,
                                source_file=source_file)
                            for stdin in stdins]
            results['status'] = 'success'
            results['runs'] = run_results
            return results

        finally:
            shutil.rmtree(source_dir)

    def default_apparmor_profile(self):
        return self.config.APPARMOR_PROFILES["compiled"]
