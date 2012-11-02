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
    returncode  = 0,
    error       = None)
