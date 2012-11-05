from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

fortran = Language('Fortran',
    profile             = exec_profiles.CompilerProfile(straitjacket_settings),
    binary              = 'gfortran',
    filename            = 'source.f90',
    apparmor_profile    = 'straitjacket/compiler/default')
# Disable fortran until I can sort out how to get it working
fortran.enabled = False

LanguageTest('test-simple', fortran,
    source      = ( 'PRINT *, "yay fortran"                                      \n'
                    'END                                                         \n'
                  ),
    stdout      = ' yay fortran\n',
    stderr      = '',
    returncode  = 0,
    error       = None)

LanguageTest('test-rlimit', fortran,
    source      = ( 'program rlimittest                                          \n'
                    'print *, "starting allocation"                              \n'
                    'call rlimit(1073741824)                                     \n'
                    'print *, "finished allocation"                              \n'
                    'end                                                         \n'
                    'subroutine rlimit(ilen)                                     \n'
                    'implicit double precision (a-h,o-z), integer (i-n)          \n'
                    'dimension iarray(ilen), array(ilen)                         \n'
                    'parameter (ZERO = 0.0d0)                                    \n'
                    'do 100 i=1,ilen                                             \n'
                    'iarray(i) = i                                               \n'
                    'array(i) = ZERO                                             \n'
                    '100 continue                                                \n'
                    'end                                                         \n'
                  ),
    stdout      = ' starting allocation\n',
    stderr      = '',
    returncode  = -11,
    error       = 'runtime_error')

LanguageTest('test-apparmor', fortran,
    source      = ( 'program apparmortest                                        \n'
                    'open(unit=1, file="/etc/hosts")                             \n'
                    'read(1, *) x, y                                             \n'
                    'close(1)                                                    \n'
                    'end                                                         \n'
                  ),
    stdout      = '',
    stderr      = 'Permission denied trying to open file "/etc/hosts"',
    returncode  = 2,
    error       = 'runtime_error')

