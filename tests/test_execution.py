def _execute(webapp, params):
    return webapp.request('/execute', 'POST', urllib.urlencode(params))

def test_bad_language(webapp):
    response = _execute(webapp, {
        'language'  : 'non-existent-language',
        'source'    : '',
        'stdin'     : ''})
    assert response.status == '400 Bad Request'

def test_too_long_execution(language, webapp):
    response = _execute_and_parse({
        'langauge'  : 'ruby1.8',
        'source'    : 'sleep 20',
        'stdin'     : ''
    })
    assert response['stdout'] == ''
    assert response['stderr'] == ''
    assert response['return_code'] == -9
    assert response['status'] == 'runtime_timelimit'



def testOkayExecution(language, webapp):
    self.execute({
            "language": "ruby1.8",
            "source": "sleep 10\n",
            "stdin": ""},
        "",
        "",
        0,
        "")

def testLimitedExecution(language, webapp):
    self.execute({
            "language": "ruby1.8",
            "source": "sleep 10\n",
            "stdin": "",
            "timelimit": "1.5"},
        "",
        "",
        -9,
        "runtime_timelimit")

def testOkayLimitedExecution(language, webapp):
    self.execute({
            "language": "ruby1.8",
            "source": "sleep 1\n",
            "stdin": "",
            "timelimit": "2.5"},
        "",
        "",
        0,
        "")
