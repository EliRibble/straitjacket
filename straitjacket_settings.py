# The maximum runtime for a single request
# This time will be used for everything, compilation, 
# all of the runs of the program, everything. This is
# so that our nginx reverse proxy doesn't time out
# This means that if the user passes in 100 values for
# stdin then we must run the program 100 times within
# this time out
MAX_RUNTIME = 54

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
