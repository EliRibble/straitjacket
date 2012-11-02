from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

guile = Language('Guile',
    profile             = exec_profiles.InterpreterProfile(straitjacket_settings),
    binary              = 'guile',
    filename            = 'source.scm',
    apparmor_profile    = 'straitjacket/interpreter/guile')

LanguageTest('test-simple', guile,
    source      = ( '(begin (display "hi from guile") (newline))                 \n'
                  ),
    stdout      = 'hi from guile\n',
    stderr      = '',
    returncode  = 0,
    error       = None)

LanguageTest('test-apparmor', guile,
    source      = ( '(with-input-from-file "/etc/passwd" (lambda ()              \n'
                    '(define loop (lambda (token)                                \n'
                    '(if (not (eof-object? token))                               \n'
                    '(begin (display token) (newline) (loop (read))))))          \n'
                    '(loop (read))))                                             \n'
                  ),
    stdout      = '',
    stderr      = 'ERROR: In procedure open-file:\nERROR: Permission denied: "/etc/passwd"\n',
    returncode  = 1,
    error       = 'runtime_error')

LanguageTest('test-rlimit', guile,
    source      = ( '(begin (display (make-string 1073741824)) (newline))        \n'
                  ),
    stdout      = '',
    stderr      = 'FATAL: memory error in realloc\n',
    returncode  = -6,
    error       = 'runtime_error')

