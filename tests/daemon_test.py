"""
COSC364 - RIP Programming Assignment
- daemon_test.py

Created: 
- 21/02/25

Authors: 
- Martyn Gascoigne 
- Max Moir
"""

import socket
import pytest
from src.daemon import Daemon

@pytest.fixture(name='daemon')
def fixture_cfg1_daemon():
    ''' 
    Create daemon from config cfg1
    
    '''
    return Daemon('id', './tests/cfgs/cfg1.txt')

def test_creation(daemon):
    ''' 
    Test daemon creation
    '''
    assert daemon.inputs  == [6110, 6201, 7345]
    assert daemon.outputs == [[1234, 1, 1], [4213, 1, 1], [2143, 1, 1]]

    for sock in daemon.socks:
        assert isinstance(sock, socket.socket)
