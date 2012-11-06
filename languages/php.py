from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

php = Language('PHP',
    profile             = exec_profiles.InterpreterProfile(straitjacket_settings),
    binary              = 'php5',
    filename            = 'source.php',
    apparmor_profile    = 'straitjacket/interpreter/default')

LanguageTest('test-simple', php,
    source      = ( '<? echo "hi from php" ?>                                    \n'
                  ),
    stdout      = 'hi from php',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-apparmor', php,
    source      = ( '<? $fh = fopen("/etc/hosts", "r");                          \n'
                    'echo fread($fh, filesize("/etc/hosts"));                    \n'
                    'fclose($fh) ?>                                              \n'
                  ),
    stdout      = '\nWarning: fopen\(/etc/hosts\): failed to open stream: Permission denied in',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-rlimit', php,
    source      = ( '<? echo pcntl_fork(); ?>                                    \n'
                  ),
    stdout      = '\nWarning: pcntl_fork\(\): Error 11',
    stderr      = '',
    returncode  = 0)

