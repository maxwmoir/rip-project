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
import time
import pytest
from src.daemon import Daemon
from src.routing_table import RoutingTable


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
    

# TODO Write tests for bad cases:

def print_system_graph(daemons):
    """ 
    Helper function to graph the routing tables of each router in a list, print it out, and return it.
    """
    graph = [[(-1, -1) for x in range(7)] for x in range(7)]
    for i, d in enumerate(daemons):
        for route in d.table.routes.values():
            graph[i][route.destination - 1] = (route.next_hop, route.metric)

    table_str = ["", "", "", "", "", "", "", "", ""]
    for i, router in enumerate(graph): 
        table_str[0] += f"    Router {i + 1}      "
        table_str[1] += f"dest next metric  "
        
        for d in range(7):
            if graph[i][d][0] == -1:
                table_str[2 + d] += f" {d + 1:2d}    -    -     "
            else:
                table_str[2 + d] += f" {d + 1:2d}   {graph[i][d][0]:2d}   {graph[i][d][1]:2d}     "

    print("\n".join(table_str))
    return graph


def test_final_graph():
    '''
    FINAL GRAPH
    '''
    print()

    daemons = [Daemon(f"./tests/cfgs/figure1/cfg{i + 1}.txt") for i in range(7)]

    for d in daemons:
        for sock in d.socks:
            assert isinstance(sock, socket.socket)
            assert len(d.inputs) == len(d.outputs)

    threads = []

    for d in daemons:
        thread = threading.Thread(target=d.start)
        threads.append(thread)
        thread.start()

    correct_answers = [
        [[(1, 0), (2, 1), (2, 4), (6, 8), (6, 6), (6, 5), (7, 8)], [(1, 1), (2, 0), (3, 3), (3, 7), (1, 7), (1, 6), (1, 9)], [(2, 4), (2, 3), (3, 0), (4, 4), (4, 6), (4, 7), (4, 10)], [(5, 8), (3, 7), (3, 4), (4, 0), (5, 2), (5, 3), (7, 6)], [(6, 6), (6, 7), (4, 6), (4, 2), (5, 0), (6, 1), (4, 8)], [(1, 5), (1, 6), (5, 7), (5, 3), (5, 1), (6, 0), (5, 9)], [(1, 8), (1, 9), (4, 10), (4, 6), (4, 8), (4, 9), (7, 0)]],
        [[(1, 0), (2, 1), (2, 4), (6, 8), (6, 6), (6, 5), (7, 8)], [(1, 1), (2, 0), (3, 3), (3, 7), (1, 7), (1, 6), (1, 9)], [(2, 4), (2, 3), (3, 0), (4, 4), (4, 6), (4, 7), (4, 10)], [(3, 8), (3, 7), (3, 4), (4, 0), (5, 2), (5, 3), (7, 6)], [(6, 6), (6, 7), (4, 6), (4, 2), (5, 0), (6, 1), (4, 8)], [(1, 5), (1, 6), (5, 7), (5, 3), (5, 1), (6, 0), (5, 9)], [(1, 8), (1, 9), (4, 10), (4, 6), (4, 8), (4, 9), (7, 0)]],
        [[(1, 0), (2, 1), (2, 4), (2, 8), (6, 6), (6, 5), (7, 8)], [(1, 1), (2, 0), (3, 3), (3, 7), (1, 7), (1, 6), (1, 9)], [(2, 4), (2, 3), (3, 0), (4, 4), (4, 6), (4, 7), (4, 10)], [(3, 8), (3, 7), (3, 4), (4, 0), (5, 2), (5, 3), (7, 6)], [(6, 6), (6, 7), (4, 6), (4, 2), (5, 0), (6, 1), (4, 8)], [(1, 5), (1, 6), (5, 7), (5, 3), (5, 1), (6, 0), (5, 9)], [(1, 8), (1, 9), (4, 10), (4, 6), (4, 8), (4, 9), (7, 0)]],
        [[(1, 0), (2, 1), (2, 4), (2, 8), (6, 6), (6, 5), (7, 8)], [(1, 1), (2, 0), (3, 3), (3, 7), (1, 7), (1, 6), (1, 9)], [(2, 4), (2, 3), (3, 0), (4, 4), (4, 6), (4, 7), (4, 10)], [(5, 8), (3, 7), (3, 4), (4, 0), (5, 2), (5, 3), (7, 6)], [(6, 6), (6, 7), (4, 6), (4, 2), (5, 0), (6, 1), (4, 8)], [(1, 5), (1, 6), (5, 7), (5, 3), (5, 1), (6, 0), (5, 9)], [(1, 8), (1, 9), (4, 10), (4, 6), (4, 8), (4, 9), (7, 0)]],
    ]


    time.sleep(5)

    print()
    graph = print_system_graph(daemons)    
    print("Table correct:", graph in correct_answers)
    assert graph in correct_answers
    
    print("\nKilling node 4\n")
    daemons[3].running = False
    daemons[3].table = RoutingTable()

    time.sleep(10)
    graph = print_system_graph(daemons)

    correct_no_4 = [[(1, 0), (2, 1), (2, 4), (-1, -1), (6, 6), (6, 5), (7, 8)], [(1, 1), (2, 0), (3, 3), (-1, -1), (1, 7), (1, 6), (1, 9)], [(2, 4), (2, 3), (3, 0), (-1, -1), (2, 10), (2, 9), (2, 12)], [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)], [(6, 6), (6, 7), (6, 10), (-1, -1), (5, 0), (6, 1), (6, 14)], [(1, 5), (1, 6), (1, 9), (-1, -1), (5, 1), (6, 0), (1, 13)], [(1, 8), (1, 9), (1, 12), (-1, -1), (1, 14), (1, 13), (7, 0)]] 

    correct = True 
    for r, row in enumerate(correct_no_4):
        for c, col in enumerate(row):
            if graph[r][c] != col:
                correct = False
    print("Table correct:", correct)
        
    print("\nRestarting node 4\n")
    daemons[3].running = True
    thread = threading.Thread(target=daemons[3].start)
    threads.append(thread)
    thread.start()
    
    time.sleep(10)

    graph = print_system_graph(daemons)
    print("Table correct:", graph in correct_answers)
    assert(graph in correct_answers)