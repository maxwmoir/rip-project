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
import threading
import pytest
from src.daemon import Daemon
from src import packet
from src.packet import RIPEntry, RIPPacket


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


def test_connection():
    '''
    Test Connection
    '''

    d1 = Daemon('id', './tests/cfgs/cfg2.txt')
    d2 = Daemon('id', './tests/cfgs/cfg3.txt')

    assert 6110 in d1.inputs
    assert [6110, 1, 1] in d2.outputs

    for sock in d1.socks:
        assert isinstance(sock, socket.socket)

    ents = [
        RIPEntry(2, 3),
        RIPEntry(3, 6),
        RIPEntry(5, 5),
        RIPEntry(1, 2),
    ]

    a_packet = RIPPacket(packet.COMMAND_RESPONSE, 2, ents)

    encoded_packet = packet.encode_packet(a_packet)

    t1 = threading.Thread(target=d1.rcv_loop)
    t2 = threading.Thread(target=d2.send_message, args=(encoded_packet,))

    # decoded_packet = packet.decode_packet(encoded_packet)
    t1.start()
    t2.start()
