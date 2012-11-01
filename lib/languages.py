import subprocess
import re

from lib import exec_profiles
import straitjacket_settings

class Language(object):
    def __init__(self, name, profile, binary, filename, options=None, visible_name=None, version=None, version_switch=None, vm_command=None,
            compiler_apparmor_profile   = None,
            vm_apparmor_profile         = None,
            compilation_command         = None
        ):
        self.name                       = name
        self.profile                    = profile
        self.binary                     = binary
        self.filename                   = filename
        self.options                    = options if options else []
        self.visible_name               = visible_name if visible_name else '{0} ({1})'.format(name, binary + ' '.join(self.options))
        self.version_switch             = version_switch if version_switch else "--version"
        self.version                    = version if version else self.get_version()
        self.interpretation_command     = None
        self.vm_command                 = vm_command
        self.compiler_apparmor_profile  = compiler_apparmor_profile
        self.vm_apparmor_profile        = vm_apparmor_profile
        self.compilation_command        = None
        self.tests                      = []

    def get_version(self):
        proc = subprocess.Popen([self.binary, self.version_switch], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = proc.communicate()
        return stdout.split('\n')[0]

    def is_enabled(self):
        return True

    def execute(self, source, stdin, timelimit=None):
        return self.profile.run(self, source, stdin, custom_timelimit=timelimit)

class LanguageTest(object):
    def __init__(self, name, language, source, stdout, stderr, returncode, error):
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

bash = Language('Bash', exec_profiles.InterpreterProfile(straitjacket_settings), binary='bash', filename='source.sh')
LanguageTest('test-simple', bash,
     source     = 'echo -n hello from bash',
     stdout     = 'hello from bash',
     stderr     = '',
     returncode = 0,
     error      = None)
LanguageTest('test-apparmor', bash,
     source     = 'while read line; do echo -e "$line\n"; done < /etc/hosts',
     stdout     = '',
     stderr     = 'line 2: /etc/hosts: Permission denied',
     returncode = 1,
     error      = 'runtime_error')
LanguageTest('test-rlimit', bash,
     source     = (
        'fork() {                   \n'
        '   echo "hi from child"    \n'
        '}                          \n'
        'fork & fork & fork &       \n'
        'wait'),
     stdout     = '',
     stderr     = 'fork: retry: No child processes',
     returncode = 254,
     error      = 'runtime_error')

c_sharp = Language('C#',
    profile                     = exec_profiles.VMProfile(straitjacket_settings),
    binary                      = 'gmcs',
    filename                    = 'source.cs',
    version_switch              = '--version',
    compilation_command         = lambda source: ["mono", "/usr/lib/mono/2.0/gmcs.exe", "-out:main.exe", source],
    vm_command                  = lambda source: ['env', "LD_PRELOAD=/var/local/straitjacket/lib/getpwuid_r_hijack.so", "mono", "main.exe"],
    compiler_apparmor_profile   = 'straitjacket/compiler/csharp',
    vm_apparmor_profile         = 'straitjacket/compiled/csharp'
)
LanguageTest('test-simple', c_sharp,
    source      = ( 'public class HelloWorld {                              \n'
                    '  public static void Main() {                          \n'
                    '    System.Console.WriteLine("hey c# world, sup?");    \n'
                    '  }                                                    \n'
                    '}'),
    stdout      = 'hey c# world, sup?\n',
    stderr      = '',
    returncode  = 0,
    error       = None)


def all():
    from lib import languages
    found = []
    for key in dir(languages):
        item = getattr(languages, key)
        if isinstance(item, Language):
            found.append(item)
    return found

def get(language_name):
    from lib import languages
    try:
        return getattr(languages, language_name)
    except AttributeError:
        for language in all():
            if language.name == language_name:
                return language
        raise Exception("No language named '{0}' found".format(language_name))
    except TypeError:
        return (get(n) for n in language_name)
        
