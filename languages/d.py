from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

d = Language('D',
    profile             = exec_profiles.CompilerProfile(straitjacket_settings),
    version_switch      = '--help',
    binary              = 'dmd',
    compilation_command = lambda source, obj: ['dmd', '-of%s' % obj, source],
    filename            = 'source.d',
    apparmor_profile    = 'straitjacket/compiler/dmd')

LanguageTest('test-simple', d,
    source      = ( 'import std.stdio;                                           \n'
                    'int main() {                                                \n'
                    'std.stdio.writefln("Hello from D");                         \n'
                    'return 0;                                                   \n'
                    '}                                                           \n'
                  ),
    stdout      = 'Hello from D\n',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-apparmor', d,
    source      = ( 'import std.stdio;                                           \n'
                    'import std.file;                                            \n'
                    'int main(char[][] args) {                                   \n'
                    'std.stdio.writefln("%s", cast(char[])read("/etc/hosts"));   \n'
                    'return 0;                                                   \n'
                    '}                                                           \n'
                  ),
    stdout      = '',
    stderr      = '/etc/hosts: Permission denied',
    returncode  = 1)

LanguageTest('test-rlimit', d,
    source      = ( 'import std.stdio;                                           \n'
                    'int main() {                                                \n'
                    'char[] lotsomem = new char[1073741824];                     \n'
                    'return 0;                                                   \n'
                    '}                                                           \n'
                  ),
    stdout      = '',
    stderr      = 'core.exception.OutOfMemoryError',
    returncode  = 1)

