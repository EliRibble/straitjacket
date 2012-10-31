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

