from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

clojure = Language('Clojure',
    profile                 = exec_profiles.InterpreterProfile(straitjacket_settings),
    version                 = '1.2.1',
    binary                  = 'java',
    interpretation_command  = lambda source: ['java', '-cp', '/usr/lib/clojure/clojure-1.4.0.jar:/usr/lib/clojure/clojure-1.4.0-slim.jar', 'clojure.main', source],
    filename                = 'source.clj',
    apparmor_profile        = 'straitjacket/interpreter/clojure')

LanguageTest('test-simple', clojure,
    source      = '(println "Hello from Clojure")',
    stdout      = 'Hello from Clojure',
    stderr      = '',
    returncode  = 0)
