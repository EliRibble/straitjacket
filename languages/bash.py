from languages.base import Language, LanguageTest

bash = Language('Bash',
    exec_profiles.InterpreterProfile(straitjacket_settings),
    binary='bash',
    filename='source.sh')
    
LanguageTest('test-simple', bash,
     source     = 'echo -n hello from bash',
     stdout     = 'hello from bash',
     stderr     = '',
     returncode = 0,
     error      = None)

LanguageTest('test-apparmor', bash,
     source     = 'while read line; do echo -e "$line\n"; done < /etc/hosts',
     stdout     = '',
     stderr     = 'line 2: /etc/hosts: Permission denied',
     returncode = 1,
     error      = 'runtime_error')

LanguageTest('test-rlimit', bash,
     source     = (
        'fork() {                   \n'
        '   echo "hi from child"    \n'
        '}                          \n'
        'fork & fork & fork &       \n'
        'wait'),
     stdout     = '',
     stderr     = 'fork: retry: No child processes',
     returncode = 254,
     error      = 'runtime_error')