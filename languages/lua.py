from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

lua = Language('Lua',
    profile             = exec_profiles.InterpreterProfile(straitjacket_settings),
    version_switch      = '-v',
    binary              = 'lua',
    filename            = 'source.lua',
    apparmor_profile    = 'straitjacket/interpreter/default')

LanguageTest('test-simple', lua,
    source      = ( 'print "hi from lua"                                         \n'
                  ),
    stdout      = 'hi from lua\n',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-apparmor', lua,
    source      = ( 'print(io.open("/etc/hosts", "r"))                           \n'
                  ),
    stdout      = 'nil\t/etc/hosts: Permission denied\t13\n',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-rlimit', lua,
    source      = ( 'print(os.execute("/bin/ls"))                                \n'
                  ),
    stdout      = '-1\n',
    stderr      = '',
    returncode  = 0)

