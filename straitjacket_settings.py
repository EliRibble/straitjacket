MAX_RUNTIME = 15
DIRECTORIES = {
    'temp_root' : '/var/local/straitjacket/tmp',
    'source'    : '/var/local/straitjacket/tmp/source',
    'compiler'  : '/var/local/straitjacket/tmp/compiler',
    'execution' : '/var/local/straitjacket/tmp/execute'
}

APPARMOR_PROFILES = {
    'compiled'      : 'straitjacket/compiled/default',
    'compiler'      : 'straitjacket/compiler/default',
    'interpreter'   : 'straitjacket/interpreter/default'
}
