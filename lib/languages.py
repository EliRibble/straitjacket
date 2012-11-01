import subprocess

from lib import exec_profiles

class Language(object):
    def __init__(self, name, profile, binary, filename, options=None, visible_name=None, version=None, version_switch=None):
        self.name           = name
        self.profile        = profile
        self.binary         = binary
        self.filename       = filename
        self.options        = options if options else []
        self.visible_name   = visible_name if visible_name else '{0} ({1})'.format(name, binary + ' '.join(self.options))
        self.version_switch = version_switch if version_switch else "--version"
        self.version        = version if version else self.get_version()
        self.tests          = []

    def get_version(self):
        proc = subprocess.Popen([self.binary, self.version_switch], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = proc.communicate()
        return stdout.split('\n')[0]

    def is_enabled(self):
        return True

    def execute(self, source, stdin, timelimit=None):
        return self.profile.run(self, source, stdin, custom_timelimit=timelimit)

class LanguageTest(object):
    def __init__(self, name, language, source, stdout, stderr, exitstatus, error):
        self.name       = name
        self.language   = language
        self.source     = source
        self.stdin      = None
        self.stdout     = stdout
        self.stderr     = stderr
        self.exitstatus = exitstatus
        self.error      = error

        self.language.tests.append(self)
        
    def passes(self):
        result = self.language.execute( self.source, self.stdin, None )
        import pytest;pytest.set_trace()

bash = Language('Bash', exec_profiles.InterpreterProfile, binary='bash', filename='source.sh')
LanguageTest('test-simple', bash, source='echo -n hello from bash', stdout='hello from bash', stderr='', exitstatus=0, error=None)

def all():
    from lib import languages
    found = []
    for key in dir(languages):
        item = getattr(languages, key)
        if isinstance(item, Language):
            found.append(item)
    return found
