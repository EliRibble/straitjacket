import os
import sys
import logging
import pytest
sys.path.append( os.path.abspath( os.path.join( os.path.dirname( __file__ ), '..' ) ) )

import server
import languages

logging.getLogger().setLevel(logging.DEBUG)

@pytest.fixture
def webapp():
    wrapper = server.straitjacket.StraitJacket()
    webapp = server.webapp(wrapper)
    return webapp

def pytest_addoption(parser):
    parser.addoption('--languages', action='store', dest='languages', default=None, help="Run only the provided language")
    parser.addoption('--test', action='store', dest='test', default=None, help='Run only the specified test')

def pytest_generate_tests(metafunc):
    if 'do_json' in metafunc.fixturenames:
        metafunc.parametrize('do_json', (False, True))

    if 'language' in metafunc.fixturenames:
        if metafunc.config.option.languages:
            test_languages = languages.get(metafunc.config.option.languages.split(','))
        else:
            test_languages = languages.all()

        if 'test_number' in metafunc.fixturenames:
            test_params = []
            for language in test_languages:
                if not language.is_enabled():
                    continue
                if metafunc.config.option.test is not None:
                    test_params.append((language, int(metafunc.config.option.test)))
                else:
                    for i in range(len(language.tests)):
                        test_params.append((language, i))
            metafunc.parametrize(('language', 'test_number'), test_params)
        else:
            metafunc.parametrize('language', languages)
