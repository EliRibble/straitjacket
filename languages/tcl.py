from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

class TclLanguage(Language):
    def get_version(self):
        return self.execute( "puts $tcl_version", None, None )['runs'][0]['stdout'].rstrip()

tcl = TclLanguage('Tcl',
    profile             = exec_profiles.InterpreterProfile(straitjacket_settings),
    binary              = 'tclsh',
    filename            = 'source.tcl',
    #interpretation_command  = lambda source: ['head', '/etc/passwd'],
    apparmor_profile    = 'straitjacket/interpreter/tcl')

    #apparmor_profile    = '/usr/bin/tclsh8.5')

LanguageTest('test-simple', tcl,
    source      = 'puts "hello from tcl"',
    stdout      = 'hello from tcl',
    stderr      = '',
    returncode  = 0,
    error       = None)

LanguageTest('test-apparmor', tcl,
    source      = ( 'open FILE, "/etc/hosts" or die $!;                          \n'
                    'while (<FILE>) {                                            \n'
                    'print $_;                                                   \n'
                    '}                                                           \n'
                  ),
    stdout      = '',
    stderr      = 'Permission denied at',
    returncode  = 13,
    error       = 'runtime_error')

LanguageTest('test-rlimit', tcl,
    source      = ( 'my $pid = fork();                                           \n'
                    'if(defined $pid) { print "defined"; }                       \n'
                    'else { print "undefined"; }                                 \n'
                    'print $pid;                                                 \n'
                  ),
    stdout      = 'undefined',
    stderr      = '',
    returncode  = 0,
    error       = None)

