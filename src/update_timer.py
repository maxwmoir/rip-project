"""
COSC364 - RIP Programming Assignment
- update_timer.py

Created: 
- 25/02/25

Authors: 
- Martyn Gascoigne
- Max Moir
"""

import time

class UpdateTimer():
    """
    Class that implements a periodic update timer
    """

    def __init__(self, interval, function):
        self.running = False
        self.start_time = None
        self.interval = interval
        self.function = function

    def start(self):
        """ 
        Start the update timer
        """
        self.start_time = time.time()