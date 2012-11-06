from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

scheme = Language('Scheme',
    visible_name            = 'Scheme (plt-r5rs)',
    profile                 = exec_profiles.InterpreterProfile(straitjacket_settings),
    binary                  = 'racket',
    interpretation_command  = lambda source: ['plt-r5rs', source],
    filename                = 'source.scm',
    apparmor_profile        = 'straitjacket/interpreter/racket')

LanguageTest('test-simple', scheme,
    source      = ( '(display "hi from scheme")                                  \n'
                    '(newline)                                                   \n'
                  ),
    stdout      = 'hi from scheme\n',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-apparmor', scheme,
    source      = ( '(with-input-from-file "/etc/passwd" (lambda ()              \n'
                    '(define loop (lambda (token)                                \n'
                    '(if (not (eof-object? token))                               \n'
                    '(begin (display token) (newline) (loop (read))))))          \n'
                    '(loop (read))))                                             \n'
                  ),
    stdout      = '',
    stderr      = 'with-input-from-file: cannot open input file: "/etc/passwd" \(Permission denied; errno=13\)\n',
    returncode  = 1)

LanguageTest('test-rlimit', scheme,
    source      = ( '(begin (display (make-string 1073741824)) (newline))        \n'
                  ),
    stdout      = '',
    stderr      = 'out of memory',
    returncode  = -6)

