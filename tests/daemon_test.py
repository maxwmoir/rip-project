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
import time
from src.daemon import Daemon
from src import packet
from src.packet import RIPEntry, RIPPacket


@pytest.fixture(name='daemon')
def fixture_cfg1_daemon():
    ''' 
    Create daemon from config cfg1
    
    '''
    return Daemon('./tests/cfgs/cfg1.txt')

def test_creation(daemon):
    ''' 
    Test daemon creation
    '''
    # assert daemon.inputs  == [6110, 6201, 7345]
    # assert daemon.outputs == [[1234, 1, 1], [4213, 1, 1], [2143, 1, 1]]

    for sock in daemon.socks:
        assert isinstance(sock, socket.socket)


def test_connection():
    '''
    Test Connection
    '''
    print()

    d0 = Daemon('./tests/cfgs/cfg0.txt')
    d1 = Daemon('./tests/cfgs/cfg1.txt')
    d2 = Daemon('./tests/cfgs/cfg2.txt')
    d3 = Daemon('./tests/cfgs/cfg3.txt')
    daemons = [d0, d1, d2, d3]

    for d in daemons:
        for sock in d.socks:
            assert isinstance(sock, socket.socket)
            assert len(d.inputs) == len(d.outputs)

    threads = []

    print()
    for d in daemons:
        thread = threading.Thread(target=d.main_loop)
        threads.append(thread)
        thread.start()



    # return
    # ents = [
    #     RIPEntry(2, 3),
    #     RIPEntry(3, 6),
    #     RIPEntry(5, 5),
    #     RIPEntry(1, 2),
    # ]

    # a_packet = RIPPacket(packet.COMMAND_RESPONSE, 2, ents)

    # encoded_packet = packet.encode_packet(a_packet)


    # t1 = threading.Thread(target=d1.main_loop)
    # t2 = threading.Thread(target=d2.main_loop)
    
    # t1.start()
    # t2.start()

    # for i in range(3):
    #     time.sleep(2)
    #     d2.send_packet(encoded_packet)

    # time.sleep(3)

    # d2.send_packet(packet.encode_packet(RIPPacket(3, 2, [])))

    # time.sleep(1)

    # assert len(d1.history) == 4
    # assert len(d2.history) == 0