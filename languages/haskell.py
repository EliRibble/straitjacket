from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

haskell = Language('Haskell',
    profile             = exec_profiles.CompilerProfile(straitjacket_settings),
    binary              = 'ghc',
    filename            = 'source.hs',
    apparmor_profile    = 'straitjacket/compiler/ghc')

LanguageTest('test-simple', haskell,
    source      = ( 'main = putStrLn "hello from haskell"                        \n'
                  ),
    stdout      = 'hello from haskell\n',
    stderr      = '',
    returncode  = 0,
    error       = None)

LanguageTest('test-apparmor', haskell,
    source      = ( 'main = do                                                   \n'
                    's <- readFile "/etc/hosts"                                  \n'
                    'putStrLn s                                                  \n'
                  ),
    stdout      = '',
    stderr      = '/etc/hosts: openFile: permission denied \(Permission denied\)',
    returncode  = 1,
    error       = 'runtime_error')

LanguageTest('test-rlimit', haskell,
    source      = ( 'import Control.Monad                                        \n'
                    'import System.Posix.Process                                 \n'
                    'method = putStrLn "hello from child"                        \n'
                    'main = forkProcess method                                   \n'
                  ),
    stdout      = '',
    stderr      = 'forkProcess: resource exhausted \(Resource temporarily unavailable\)',
    returncode  = 1,
    error       = 'runtime_error')

