MAX_RUNTIME = 15
DIRECTORIES = {
    'temp_root' : '/var/local/straitjacket/tmp',
    'source'    : '%(temp_root)s/source',
    'compiler'  : '%(temp_root)s/compiler',
    'execution' : '%(temp_root)s/execute'
}

APPARMOR_PROFILES = {
    'compiled'      : 'straitjacket/compiled/default',
    'compiler'      : 'straitjacket/compiler/default',
    'interpreter'   : 'straitjacket/interpreter/default'
}
