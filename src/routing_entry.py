"""
COSC364 - RIP Programming Assignment
- routing_entry.py

Created: 
- 18/02/25

Authors: 
- Martyn Gascoigne
- Max Moir
"""

class RoutingEntry():
    """
    Class for storing information about a routing connection.
    """

    def __init__(self, destination, next_hop, num_hops):
        """
        Initialise a new routing table entry.

        Args:
            destination (int): The port number of the destination router
            next_hop (int): The port number of the next router in-sequence
            num_hops (int): The cost to reach the next router
        """

        self.destination = destination
        self.next_hop = next_hop
        self.num_hops = num_hops
        # ...
