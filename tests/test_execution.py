import urllib
import json

def _execute(webapp, params):
    return webapp.request('/execute', 'POST', urllib.urlencode(params))

def _execute_and_parse(webapp, params):
    response = _execute(webapp, params)
    assert response.status == '200 OK'
    return json.loads(response['data'])

def test_bad_language(webapp):
    response = _execute(webapp, {
        'language'  : 'non-existent-language',
        'source'    : '',
        'stdin'     : ''})
    assert response.status == '400 Bad Request'

def test_too_long_execution_default(webapp):
    response = _execute_and_parse(webapp, {
        'language'  : 'Ruby 1.8',
        'source'    : 'sleep 20',
        'stdin'     : ''
    })
    assert response['stdout'] == ''
    assert response['stderr'] == ''
    assert response['returncode'] == -9
    assert response['error'] == 'runtime_timelimit'

def test_too_long_execution_custom(webapp):
    response = _execute_and_parse(webapp, {
        'language'  : 'Ruby 1.8',
        'source'    : 'sleep 3',
        'stdin'     : '',
        'timelimit' : 2
    })
    assert response['stdout'] == ''
    assert response['stderr'] == ''
    assert response['returncode'] == -9
    assert response['error'] == 'runtime_timelimit'

def test_null_execution(webapp):
    response = _execute_and_parse(webapp, {
        'language'  : 'Python',
        'source'    : '',
        'stdin'     : '',
    })
    assert response['stdout'] == ''
    assert response['stderr'] == ''
    assert response['returncode'] == 0
    assert response['error'] == None

def test_simple_execution(webapp):
    response = _execute_and_parse(webapp, {
        'language'  : 'Python',
        'source'    : 'print("Hello")',
        'stdin'     : '',
    })
    assert response['stdout'] == 'Hello\n'
    assert response['stderr'] == ''
    assert response['returncode'] == 0
    assert response['error'] == None

def test_simple_stdin(webapp):
    response = _execute_and_parse(webapp, {
        'language'  : 'Python',
        'source'    : 'import sys;print("I read " + sys.stdin.read() + " from stdin")',
        'stdin'     : 'some input',
    })
    assert response['stdout'] == 'I read some input from stdin\n'
    assert response['stderr'] == ''
    assert response['returncode'] == 0
    assert response['error'] == None
