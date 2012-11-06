from languages.base import Language, LanguageTest
from lib import exec_profiles
import straitjacket_settings

objective_c = Language('Objective-C',
    profile                     = exec_profiles.CompilerProfile(straitjacket_settings),
    binary                      = 'gcc',
    compilation_command         = lambda source, compiler_file: ['gcc', source, '-lobjc', '-fconstant-string-class=NSConstantString', '-lgnustep-base', '-o', compiler_file],
    apparmor_profile            = 'straitjacket/compiler/objective-c',
    compiled_apparmor_profile   = 'straitjacket/compiled/default',
    filename                    = 'source.m',)
    
LanguageTest('test-simple', objective_c,
    source      = ( '#include <stdio.h>                         \n'
                    'int main(int argc, char** argv) {          \n'
                    '   printf("obj-c compilation succeeded");  \n'
                    '   return 0;                               \n'
                    '}'),
    stdout      = 'obj-c compilation succeeded',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-rlimit', objective_c,
    source      = ( '#include <stdio.h>                         \n'
                    'int main(int argc, char** argv) {          \n'
                    '   printf("forked: %d", fork());           \n'
                    '   return 3;                               \n'
                    '}'),
    stdout      = 'forked: -1',
    stderr      = '',
    returncode  = 3)


LanguageTest('test-apparmor', objective_c,
    source      = ( '#include <stdio.h>                         \n'
                    '#include <errno.h>                         \n'
                    'int main(int argc, char** argv) {          \n'
                    '   if(fopen("/etc/hosts", "r")) {          \n'
                    '       printf("opened");                   \n'
                    '   } else {                                \n'
                    '       printf("not opened: %d", errno);    \n'
                    '   }                                       \n'
                    '   return 0;                               \n'
                    '}'),
    stdout      = 'not opened: 13',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-argv0', objective_c,
    source      = ( '#include <stdio.h>                 \n'
                    'int main(int argc, char** argv) {  \n'
                    '   printf("%s", argv[0]);          \n'
                    '   return 0;                       \n'
                    '}'),
    stdout      = 'straitjacket-binary',
    stderr      = '',
    returncode  = 0)

LanguageTest('test-includesafe', objective_c,
    source      = ( '#include "/etc/hosts"                          \n'
                    'int main(int argc, char** argv) { return 0; }'),
    stdout      = 'fatal error: /etc/hosts: Permission denied\n',
    returncode  = 1,
    status      = 'compilation failed')
