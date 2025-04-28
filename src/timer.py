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
    """
    Class to represent the state of the timer.
    """

    RUNNING = "RUNNING"
    PAUSED  = "PAUSED"


class Timer():
    """
    Class to represent a Timer.
    """

    def __init__(self):
        """
        Initialize the Timer.
        """

        self.state = State.PAUSED
        self.start_time = 0.0
        self.creation_time = time.time()

        # Optional callback function called each period 
        self.callback = None
        self.period = None
    
    def get_uptime(self):
        """
        Returns timer uptime.

        Returns:
            float: Time since last start.
        """

        return time.time() - self.start_time 
        
    def reset(self):
        """
        Resets the timer.
        """

        if self.state is State.RUNNING:
            self.start_time = time.time()


    def start(self):
        """
        Starts the timer.
        """

        self.state = State.RUNNING
        self.time = time.time()