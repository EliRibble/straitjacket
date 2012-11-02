from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

ruby_18 = Language('Ruby',
    profile             = exec_profiles.InterpreterProfile(straitjacket_settings),
    binary              = 'ruby1.8',
    filename            = 'source.rb',
    apparmor_profile    = 'straitjacket/interpreter/ruby1.8')

LanguageTest('test-simple', ruby_18,
    source      = ( 'puts "hi from ruby"                                         \n'
                  ),
    stdout      = 'hi from ruby\n',
    stderr      = '',
    returncode  = 0,
    error       = None)

LanguageTest('test-apparmor', ruby_18,
    source      = ( 'puts File.read("/etc/hosts")                                \n'
                  ),
    stdout      = '',
    stderr      = 'Permission denied - /etc/hosts \(Errno::EACCES\)',
    returncode  = 1,
    error       = 'runtime_error')

LanguageTest('test-rlimit', ruby_18,
    source      = ( 'puts fork                                                   \n'
                  ),
    stdout      = '',
    stderr      = "in `fork': Resource temporarily unavailable - fork\(2\) \(Errno::EAGAIN\)",
    returncode  = 1,
    error       = 'runtime_error')

