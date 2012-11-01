import os
import sys
import pytest
sys.path.append( os.path.abspath( os.path.join( os.path.dirname( __file__ ), '..' ) ) )

import server
from lib import languages

@pytest.fixture
def webapp():
    wrapper = server.straitjacket.StraitJacket(server.DEFAULT_CONFIG_DIR)
    webapp = server.webapp(wrapper)
    return webapp

def pytest_addoption(parser):
    parser.addoption('--languages', action='store', dest='languages', default=None, help="Run only the provided language")

def pytest_generate_tests(metafunc):
    if 'language' in metafunc.fixturenames:
        if metafunc.config.option.languages:
            test_languages = languages.get(metafunc.config.option.languages.split(','))
        else:
            test_languages = languages.all()

        if 'test_number' in metafunc.fixturenames:
            test_params = []
            for language in test_languages:
                for i in range(len(language.tests)):
                    test_params.append((language, i))
            metafunc.parametrize(('language', 'test_number'), test_params)
        else:
            metafunc.parametrize('language', languages)
