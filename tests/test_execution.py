import urllib
import json

def _execute(webapp, do_json, params) :
    if do_json:
        return webapp.request('/execute', 'POST', json.dumps(params))
    else:
        return webapp.request('/execute', 'POST', urllib.urlencode(params))

def _execute_and_parse(webapp, do_json, params):
    response = _execute(webapp, do_json, params)
    assert response.status == '200 OK'
    # We have no way of testing the time since it is
    # highly dependent of the system it is run on
    # so we just make sure that it is present and a float
    data = json.loads(response['data'])
    return data

def test_bad_language(webapp, do_json):
    response = _execute(webapp, do_json, {
        'language'  : 'non-existent-language',
        'source'    : '',
        'stdin'     : ''})
    assert response.status == '400 Bad Request'

def test_missing_required_parameters(webapp, do_json):
    for param in ('language', 'source'):
        good_request = {
            'language'  : 'Python',
            'source'    : 'print("hi")',
        }
        del good_request[param]
        response = _execute(webapp, do_json, good_request)
        assert response.status == '400 Bad Request'

def test_too_long_execution_default(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'Ruby 1.8',
        'source'    : 'sleep 20',
        'stdin'     : ''
    })
    response == {
        'status'        : 'timeout',
        'stdout'        : '',
        'stderr'        : '',
        'returncode'    : None,
    }

def test_too_long_execution_custom(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'Ruby 1.8',
        'source'    : 'sleep 3',
        'stdin'     : '',
        'timelimit' : 2
    })
    response == {
        'status'        : 'timeout',
        'stdout'        : '',
        'stderr'        : '',
        'returncode'    : None,
    }

def test_null_execution(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'Python',
        'source'    : '',
        'stdin'     : '',
    })
    assert response == {
        'status'        : 'success',
        'stdout'        : '',
        'stderr'        : '',
        'returncode'    : 0
    }

def test_simple_stdout(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'Python',
        'source'    : 'print("Hello")',
        'stdin'     : '',
    })
    assert response == {
        'status'        : 'success',
        'stdout'        : 'Hello\n',
        'stderr'        : '',
        'returncode'    : 0
    }

def test_simple_stderr(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'Python',
        'source'    : 'import sys;sys.stderr.write("This is stderr")',
        'stdin'     : '',
    })
    assert response == {
        'status'        : 'success',
        'stdout'        : '',
        'stderr'        : 'This is stderr',
        'returncode'    : 0
    }

def test_simple_stdin(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'Python',
        'source'    : 'import sys;print("I read " + sys.stdin.read() + " from stdin")',
        'stdin'     : 'some input',
    })
    assert response == {
        'status'        : 'success',
        'stdout'        : 'I read some input from stdin\n',
        'stderr'        : '',
        'returncode'    : 0
    }

def test_simple_returncode(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'Python',
        'source'    : 'import sys;sys.exit(12)',
        'stdin'     : '',
    })
    assert response == {
        'status'        : 'success',
        'stdout'        : '',
        'stderr'        : '',
        'returncode'    : 12 
    }

def test_compiler_error(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'C',
        'source'    : 'invalid',
        'stdin'     : '',
    })
    del response['stderr']
    assert response == {
        'status'        : 'compilation failed',
        'stdout'        : '',
        'returncode'    : 1 
    }
    
