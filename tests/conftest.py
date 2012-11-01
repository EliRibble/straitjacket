import os
import sys
import pytest
sys.path.append( os.path.abspath( os.path.join( os.path.dirname( __file__ ), '..' ) ) )

import server

@pytest.fixture
def webapp():
    wrapper = server.straitjacket.StraitJacket(server.DEFAULT_CONFIG_DIR)
    webapp = server.webapp(wrapper)
    return webapp

def pytest_addoption(parser):
    parser.addoption('--languages', action='store', dest='languages', default=None, help="Run only the provided language")

def pytest_generate_tests(metafunc):
    if metafunc.config.option.languages:
        languages = metafunc.config.option.languages.split(',')   
    else:
        languages = ['bash', 'c']

    metafunc.parametrize(('language'), languages)
