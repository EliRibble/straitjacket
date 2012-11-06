from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

ocaml = Language('OCaml',
    profile             = exec_profiles.CompilerProfile(straitjacket_settings),
    version_switch      = '-version',
    binary              = 'ocamlc',
    filename            = 'source.ml',
    apparmor_profile    = 'straitjacket/compiler/ocaml')

LanguageTest('test-simple', ocaml,
    source      = ( 'print_string "Hello from OCaml!\n";;                        \n'
                  ),
    stdout      = 'Hello from OCaml!\n',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-apparmor', ocaml,
    source      = ( 'let lines = ref [] in                                       \n'
                    'let chan = open_in "/etc/hosts" in                          \n'
                    'try                                                         \n'
                    'while true; do                                              \n'
                    'lines := input_line chan :: !lines                          \n'
                    'done; []                                                    \n'
                    'with End_of_file ->                                         \n'
                    'close_in chan;                                              \n'
                    'List.rev !lines                                             \n'
                  ),
    stdout      = '',
    stderr      = 'Fatal error: exception Sys_error\("/etc/hosts: Permission denied"\)\n',
    returncode  = 2)

LanguageTest('test-rlimit', ocaml,
    source      = ( 'let rec build_list = fun (array, x) ->                      \n'
                    'if x = 0 then                                               \n'
                    'array                                                       \n'
                    'else                                                        \n'
                    'build_list ( "x"::array, x - 1 )                            \n'
                    ';;                                                          \n'
                    'build_list ( [], 1073741824 );;                             \n'
                  ),
    stdout      = '',
    stderr      = 'Fatal error: out of memory.\n',
    returncode  = 2)

