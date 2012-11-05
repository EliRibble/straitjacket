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
    return json.loads(response['data'])

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
    assert response['stdout']       == ''
    assert response['stderr']       == ''
    assert response['returncode']   == -9
    assert response['error']        == 'runtime_timelimit'

def test_too_long_execution_custom(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'Ruby 1.8',
        'source'    : 'sleep 3',
        'stdin'     : '',
        'timelimit' : 2
    })
    assert response['stdout'] == ''
    assert response['stderr'] == ''
    assert response['returncode'] == -9
    assert response['error'] == 'runtime_timelimit'

def test_null_execution(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'Python',
        'source'    : '',
        'stdin'     : '',
    })
    assert response['stdout'] == ''
    assert response['stderr'] == ''
    assert response['returncode'] == 0
    assert response['error'] == None

def test_simple_stdout(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'Python',
        'source'    : 'print("Hello")',
        'stdin'     : '',
    })
    assert response['stdout'] == 'Hello\n'
    assert response['stderr'] == ''
    assert response['returncode'] == 0
    assert response['error'] == None

def test_simple_stderr(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'Python',
        'source'    : 'import sys;sys.stderr.write("This is stderr")',
        'stdin'     : '',
    })
    assert response['stdout'] == ''
    assert response['stderr'] == 'This is stderr'
    assert response['returncode'] == 0
    assert response['error'] == None

def test_simple_stdin(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'Python',
        'source'    : 'import sys;print("I read " + sys.stdin.read() + " from stdin")',
        'stdin'     : 'some input',
    })
    assert response['stdout'] == 'I read some input from stdin\n'
    assert response['stderr'] == ''
    assert response['returncode'] == 0
    assert response['error'] == None

def test_simple_returncode(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'Python',
        'source'    : 'import sys;sys.exit(12)',
        'stdin'     : '',
    })
    assert response['stdout'] == ''
    assert response['stderr'] == ''
    assert response['returncode'] == 12
    assert response['error'] == 'runtime_error'

def test_compiler_error(webapp, do_json):
    response = _execute_and_parse(webapp, do_json, {
        'language'  : 'C',
        'source'    : 'invalid',
        'stdin'     : '',
    })
    assert response['stdout'] == ''
    assert response['returncode'] == 1
    assert response['time'] == 0.0
    assert response['error'] == 'compilation_error'
    
