"""
COSC364 - RIP Programming Assignment
- timer.py

Created: 
- 18/02/25

Authors: 
- Martyn Gascoigne
- Max Moir
"""

import time

class State():
    RUNNING = "RUNNING"
    PAUSED  = "PAUSED"


class Timer():
    """
    Class to represent a Timer. 

    Will
    """

    def __init__(self):
        self.state = State.PAUSED
        self.start_time = 0.0
        self.creation_time = time.time()
        self.period = None

    def start(self):
        self.state = State.RUNNING
        self.time = time.time()


