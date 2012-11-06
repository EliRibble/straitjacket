
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
            version_pattern             = None,
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
        self.version_pattern            = version_pattern
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
        if self.version_pattern:
            m = re.search(self.version_pattern, stdout)
            if m:
                return m.group('version')
        return stdout.split('\n')[0]

    def is_enabled(self):
        return self.enabled

    def execute(self, source, stdin, timelimit=None):
        return self.profile.run(self, source, stdin, custom_timelimit=timelimit)

    def __repr__(self):
        return "Language {0}".format(self.name)

class LanguageTest(object):
    def __init__(self, name, language, source, stdout='', stderr='', returncode=0, status='success'):
        self.name           = name
        self.language       = language
        self.source         = source
        self.stdin          = None
        self.returncode     = returncode
        self.status         = status
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
        assert result['status'] == self.status
        if self.status == 'success':
            assert result['runs'][0]['returncode'] == self.returncode
            assert re.search( self.stdout_pattern, result['runs'][0]['stdout'] )
            assert re.search( self.stderr_pattern, result['runs'][0]['stderr'] )
        else:
            assert result['compilation']['returncode'] == self.returncode
            assert re.search( self.stdout_pattern, result['compilation']['stdout'] )
            assert re.search( self.stderr_pattern, result['compilation']['stderr'] )

    def __repr__(self):
        return "LanguageTest {0} for {1}".format(self.name, self.language)
            

