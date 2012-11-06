from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

perl = Language('Perl',
    profile             = exec_profiles.InterpreterProfile(straitjacket_settings),
    binary              = 'perl',
    version_pattern     = '\(v(?P<version>[\d\.]+)\)',
    filename            = 'source.pl',
    apparmor_profile    = 'straitjacket/interpreter/default')

LanguageTest('test-simple', perl,
    source      = ( "$message = 'hello from perl';                               \n"
                    'print "$message";                                           \n'
                  ),
    stdout      = 'hello from perl',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-apparmor', perl,
    source      = ( 'open FILE, "/etc/hosts" or die $!;                          \n'
                    'while (<FILE>) {                                            \n'
                    'print $_;                                                   \n'
                    '}                                                           \n'
                  ),
    stdout      = '',
    stderr      = 'Permission denied at',
    returncode  = 13)

LanguageTest('test-rlimit', perl,
    source      = ( 'my $pid = fork();                                           \n'
                    'if(defined $pid) { print "defined"; }                       \n'
                    'else { print "undefined"; }                                 \n'
                    'print $pid;                                                 \n'
                  ),
    stdout      = 'undefined',
    stderr      = '',
    returncode  = 0)

