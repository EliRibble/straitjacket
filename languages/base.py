
import subprocess
import re

from lib import exec_profiles
import straitjacket_settings

class Language(object):
    def __init__(self,
            name,
            profile,
            binary,
            filename,
            options                     = None,
            visible_name                = None,
            version                     = None,
            version_switch              = None,
            vm_command                  = None,
            apparmor_profile            = None,
            compiler_apparmor_profile   = None,
            compiled_apparmor_profile   = None,
            vm_apparmor_profile         = None,
            compilation_command         = None,
            interpretation_command      = None,
        ):
        self.enabled                    = True
        self.name                       = name
        self.profile                    = profile
        self.apparmor_profile           = apparmor_profile
        self.binary                     = binary
        self.filename                   = filename
        self.options                    = options if options else []
        self.visible_name               = visible_name if visible_name else '{0} ({1})'.format(name, binary + ' '.join(self.options))
        self.version_switch             = version_switch if version_switch else "--version"
        self._version                   = version
        self.interpretation_command     = interpretation_command
        self.vm_command                 = vm_command
        self.compiler_apparmor_profile  = compiler_apparmor_profile
        self.compiled_apparmor_profile  = compiled_apparmor_profile
        self.vm_apparmor_profile        = vm_apparmor_profile
        self.compilation_command        = compilation_command
        self.tests                      = []

    @property
    def version(self):
        if self._version is None:
            self._version = self.get_version()
        return self._version

    def get_version(self):
        proc = subprocess.Popen([self.binary, self.version_switch], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = proc.communicate()
        return stdout.split('\n')[0]

    def is_enabled(self):
        return self.enabled

    def execute(self, source, stdin, timelimit=None):
        return self.profile.run(self, source, stdin, custom_timelimit=timelimit)

class LanguageTest(object):
    def __init__(self, name, language, source, stdout='', stderr='', returncode=0, error=None):
        self.name           = name
        self.language       = language
        self.source         = source
        self.stdin          = None
        self.returncode     = returncode
        self.error          = error
        self.stdout_pattern = stdout
        self.stderr_pattern = stderr

        self.language.tests.append(self)
        
    def passes(self):
        try:
            self.test()
            return True
        except AssertionError:
            return False

    def test(self):
        result = self.language.execute( self.source, self.stdin, None )
        assert self.returncode == result.returncode
        assert self.error      == result.error
        assert re.search(self.stdout_pattern, result.stdout)
        assert re.search(self.stderr_pattern, result.stderr)

