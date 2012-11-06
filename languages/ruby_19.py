from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

ruby_19 = Language('Ruby 1.9',
    visible_name        = 'Ruby 1.9 (ruby1.9)',
    profile             = exec_profiles.InterpreterProfile(straitjacket_settings),
    binary              = 'ruby1.9.1',
    filename            = 'source.rb',
    apparmor_profile    = 'straitjacket/interpreter/ruby1.9')

LanguageTest('test-simple', ruby_19,
    source      = ( 'puts "hi from ruby"                                         \n'
                  ),
    stdout      = 'hi from ruby\n',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-apparmor', ruby_19,
    source      = ( 'puts File.read("/etc/hosts")                                \n'
                  ),
    stdout      = '',
    stderr      = 'Permission denied - /etc/hosts \(Errno::EACCES\)',
    returncode  = 1)

LanguageTest('test-rlimit', ruby_19,
    source      = ( 'x = [0] * 1073741824                                        \n'
                  ),
    stdout      = '',
    stderr      = 'failed to allocate memory \(NoMemoryError\)',
    returncode  = 1)

