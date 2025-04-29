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
from src.daemon import Daemon


def print_system_graph(daemons):
    """ 
    Helper function to graph the routing tables of each router, print it out, and return it.
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


def test_router_failure():
    """
    Test router convergence and failure with an example graph.
    """

    # Correct convergence and failure graphs
    correct   = [[(1, 1), (2, 1), (2, 3), (-1, -1), (-1, -1), (-1, -1), (-1, -1)], [(-1, -1), (2, 1), (2, 3), (-1, -1), (-1, -1), (-1, -1), (0, 1)], [(1, 1), (-1, -1), (3, 2), (-1, -1), (-1, -1), (-1, -1), (0, 1)], [(2, 3), (2, 2), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (2, 3)], [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)], [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)], [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)]]
    correct_f =  [[(1, 1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)], [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (0, 1)], [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)], [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)], [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)], [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)], [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)]]

    # Set up network
    daemons = [Daemon(f"./tests/cfgs/graph1/cfg{i}.txt") for i in range(4)]

    threads = []

    for d in daemons:
        thread = threading.Thread(target=d.start)
        threads.append(thread)
        thread.start()

    # Test convergence
    time.sleep(1)
    graph = print_system_graph(daemons)
    assert graph == correct

    # Disable router
    daemons[2].disable()
    time.sleep(1)
    graph = print_system_graph(daemons)
    assert graph == correct_f

    for d in daemons:
        d.shut_down()


def test_demo_graph():
    '''
    Test out the demonstration graph. 
    '''

    correct_answers = [
        [[(-1, -1), (2, 1), (2, 4), (6, 8), (6, 6), (6, 5), (7, 8)], [(1, 1), (-1, -1), (3, 3), (3, 7), (1, 7), (1, 6), (1, 9)], [(2, 4), (2, 3), (-1, -1), (4, 4), (4, 6), (4, 7), (4, 10)], [(5, 8), (3, 7), (3, 4), (-1, -1), (5, 2), (5, 3), (7, 6)], [(6, 6), (6, 7), (4, 6), (4, 2), (-1, -1), (6, 1), (4, 8)], [(1, 5), (1, 6), (5, 7), (5, 3), (5, 1), (-1, -1), (5, 9)], [(1, 8), (1, 9), (4, 10), (4, 6), (4, 8), (4, 9), (-1, -1)]],
        [[(-1, -1), (2, 1), (2, 4), (6, 8), (6, 6), (6, 5), (7, 8)], [(1, 1), (-1, -1), (3, 3), (3, 7), (1, 7), (1, 6), (1, 9)], [(2, 4), (2, 3), (-1, -1), (4, 4), (4, 6), (4, 7), (4, 10)], [(3, 8), (3, 7), (3, 4), (-1, -1), (5, 2), (5, 3), (7, 6)], [(6, 6), (6, 7), (4, 6), (4, 2), (-1, -1), (6, 1), (4, 8)], [(1, 5), (1, 6), (5, 7), (5, 3), (5, 1), (-1, -1), (5, 9)], [(1, 8), (1, 9), (4, 10), (4, 6), (4, 8), (4, 9), (-1, -1)]],
        [[(-1, -1), (2, 1), (2, 4), (2, 8), (6, 6), (6, 5), (7, 8)], [(1, 1), (-1, -1), (3, 3), (3, 7), (1, 7), (1, 6), (1, 9)], [(2, 4), (2, 3), (-1, -1), (4, 4), (4, 6), (4, 7), (4, 10)], [(3, 8), (3, 7), (3, 4), (-1, -1), (5, 2), (5, 3), (7, 6)], [(6, 6), (6, 7), (4, 6), (4, 2), (-1, -1), (6, 1), (4, 8)], [(1, 5), (1, 6), (5, 7), (5, 3), (5, 1), (-1, -1), (5, 9)], [(1, 8), (1, 9), (4, 10), (4, 6), (4, 8), (4, 9), (-1, -1)]],
        [[(-1, -1), (2, 1), (2, 4), (2, 8), (6, 6), (6, 5), (7, 8)], [(1, 1), (-1, -1), (3, 3), (3, 7), (1, 7), (1, 6), (1, 9)], [(2, 4), (2, 3), (-1, -1), (4, 4), (4, 6), (4, 7), (4, 10)], [(5, 8), (3, 7), (3, 4), (-1, -1), (5, 2), (5, 3), (7, 6)], [(6, 6), (6, 7), (4, 6), (4, 2), (-1, -1), (6, 1), (4, 8)], [(1, 5), (1, 6), (5, 7), (5, 3), (5, 1), (-1, -1), (5, 9)], [(1, 8), (1, 9), (4, 10), (4, 6), (4, 8), (4, 9), (-1, -1)]],
    ]

    correct_no_4 = [[(-1, -1), (2, 1), (2, 4), (-1, -1), (6, 6), (6, 5), (7, 8)], [(1, 1), (-1, -1), (3, 3), (-1, -1), (1, 7), (1, 6), (1, 9)], [(2, 4), (2, 3), (-1, -1), (-1, -1), (2, 10), (2, 9), (2, 12)], [(-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1), (-1, -1)], [(6, 6), (6, 7), (6, 10), (-1, -1), (-1, -1), (6, 1), (6, 14)], [(1, 5), (1, 6), (1, 9), (-1, -1), (5, 1), (-1, -1), (1, 13)], [(1, 8), (1, 9), (1, 12), (-1, -1), (1, 14), (1, 13), (-1, -1)]] 

    # Set up network
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

    # Test convergence
    time.sleep(1)

    graph = print_system_graph(daemons)

    print("Table correct:", graph in correct_answers)

    assert graph in correct_answers


    # Disable router 4

    print("\nDisabling node 4\n")
    daemons[3].disable()
    time.sleep(2)

    # Test convergence with router 4 disabled

    graph = print_system_graph(daemons)

    correct = True
    for r, row in enumerate(correct_no_4):
        for c, col in enumerate(row):
            if graph[r][c] != col:
                print(r, c)
                correct = False
    assert correct
    print("Table correct:", correct)

    # Restart router 4
    print("\nRestarting node 4\n")
    daemons[3].running = True
    thread = threading.Thread(target=daemons[3].start)
    threads.append(thread)
    thread.start()
    time.sleep(1)

    # Test convergence with router 4 restarted
    graph = print_system_graph(daemons)
    assert graph in correct_answers
    print("Table correct:", graph in correct_answers)

    # Close sockets and delete objects
    for d in daemons:
        d.shut_down()

    del threads
    del daemons
    return 