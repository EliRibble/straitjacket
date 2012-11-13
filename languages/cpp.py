from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

cpp = Language('C++',
    profile                     = exec_profiles.CompilerProfile(straitjacket_settings),
    binary                      = 'g++',
    apparmor_profile            = 'straitjacket/compiler/default',
    compiled_apparmor_profile   = 'straitjacket/compiled/default',
    filename                    = 'source.cpp')

LanguageTest('test-simple', cpp,
    source      = ( '#include <iostream>                                        \n'
                    'int main(int argc, char** argv) {                          \n'
                    '   std::cout << "compilation succeeded" << std::endl;      \n'
                    '   return 0;                                               \n'
                    '}'),
    stdout      = 'compilation succeeded')

LanguageTest('test-rlimit', cpp,
    source      = ( '#include <iostream>                                        \n'
                    'int main(int argc, char** argv) {                          \n'
                    '   std::cout << "forked: " << fork() << std::endl;         \n'
                    '   return 0;                                               \n'
                    '}'),
    stdout      = 'forked: -1')

LanguageTest('test-apparmor', cpp,
    source      = ( '#include <iostream>                                        \n'
                    '#include <stdio.h>                                         \n'
                    '#include <errno.h>                                         \n'
                    'int main(int argc, char** argv) {                          \n'
                    '   if(fopen("/etc/hosts", "r")) {                          \n'
                    '       std::cout << "opened" << std::endl;                 \n'
                    '   } else {                                                \n'
                    '       std::cout << "not opened: " << errno << std::endl;  \n'
                    '   }                                                       \n'
                    '   return 0;                                               \n'
                    '}'),
    stdout      = 'not opened: 13')

LanguageTest('test-argv0', cpp,
    source      = ( '#include <iostream>                    \n'
                    'int main(int argc, char** argv) {      \n'
                    '   std::cout << argv[0] << std::endl;  \n'
                    '   return 0;                           \n'
                    '}'),
    stdout      = 'straitjacket-binary')

LanguageTest('test-includesafe', cpp,
    source      = ( '#include "/etc/hosts"                          \n'
                    'int main(int argc, char** argv) { return 0; }' ),
    stdout      = 'fatal error: /etc/hosts: Permission denied',
    returncode  = 1,
    status      = 'compilation failed')
