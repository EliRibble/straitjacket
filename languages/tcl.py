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
    returncode  = 0)

LanguageTest('test-apparmor', tcl,
    source      = ( 'set fp [open "/etc/hosts" r]                                \n'
                    'set file_data [read $fp]                                    \n'
                    'close $fp;                                                  \n'
                    'puts $file_data;                                            \n'
                  ),
    stdout      = '',
    stderr      = 'permission denied',
    returncode  = 1)

