from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

go = Language('Go',
    profile                     = exec_profiles.CompilerProfile(straitjacket_settings),
    version_switch              = 'version',
    binary                      = 'go',
    compilation_command         = lambda source_file, output_file: ['go', 'build', '-o', output_file, source_file],
    filename                    = 'source.go',
    apparmor_profile            = 'straitjacket/compiler/go',
    compiled_apparmor_profile   = 'straitjacket/compiled/go')
    

LanguageTest('test-simple', go,
    source      = ( 'package main                                                \n'
                    'import "fmt"                                                \n'
                    'func main() {                                               \n'
                    '   fmt.Printf("Hello from Go")                              \n'
                    '}                                                           \n'
                  ),
    stdout      = 'Hello from Go',
    stderr      = '',
    returncode  = 0,
    error       = None)

LanguageTest('test-rlimit', go,
    source      = ( 'package main                                                \n'
                    'func main() {                                               \n'
                    'data := new([107374182]int)                                 \n'
                    'data[1] = 2                                                 \n'
                    '}                                                           \n'
                  ),
    stdout      = '',
    stderr      = 'out of memory',
    returncode  = 2,
    error       = 'runtime_error')

LanguageTest('test-apparmor', go,
    source      = ( 'package main                                                \n'
                    'import (                                                    \n'
                    '"os"                                                        \n'
                    '"fmt"                                                       \n'
                    ')                                                           \n'
                    'func main() {                                               \n'
                    'file, err := os.Open("/etc/hosts")                          \n'
                    'if err != nil {                                             \n'
                    'fmt.Printf("error: %s", err)                                \n'
                    'return                                                      \n'
                    '}                                                           \n'
                    'bytes := make([]byte, 4096)                                 \n'
                    'size, err := file.Read(bytes)                               \n'
                    'if err != nil {                                             \n'
                    'fmt.Printf("error: %s", err)                                \n'
                    '}                                                           \n'
                    'fmt.Printf("read: %s", bytes[:size])                        \n'
                    'file.Close()                                                \n'
                    '}                                                           \n'
                  ),
    stdout      = 'error: open /etc/hosts: permission denied',
    stderr      = '',
    returncode  = 0,
    error       = None)

