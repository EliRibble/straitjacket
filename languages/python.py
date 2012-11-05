from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

python = Language('Python',
    profile                 = exec_profiles.InterpreterProfile(straitjacket_settings),
    binary                  = 'python',
    interpretation_command  = lambda source: ['env', 'HOME=/nonexistent', 'python', source],
    filename                = 'source.py',
    apparmor_profile        = 'straitjacket/interpreter/python')

LanguageTest('test-simple', python,
    source      = ( 'print "hello from python"                                   \n'
                  ),
    stdout      = 'hello from python\n',
    stderr      = '',
    returncode  = 0,
    error       = None)

LanguageTest('test-rlimit', python,
    source      = ( 'import os                                                   \n'
                    'print os.fork()                                             \n'
                  ),
    stdout      = '',
    stderr      = 'OSError: \[Errno 11\] Resource temporarily unavailable',
    returncode  = 1,
    error       = 'runtime_error')

LanguageTest('test-apparmor', python,
    source      = ( 'print file("/etc/hosts").read()                             \n'
                  ),
    stdout      = '',
    stderr      = "Permission denied: '/etc/hosts'",
    returncode  = 1,
    error       = 'runtime_error')

