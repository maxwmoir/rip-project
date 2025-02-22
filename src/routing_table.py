"""
COSC364 - RIP Programming Assignment
- routing_table.py

Created: 
- 18/02/25

Authors: 
- Martyn Gascoigne
- Max Moir
"""

import routing_entry

class RoutingTable():
    """
    Class for storing all of the routing information for a router.
    """

    def __init__(self):
        """
        Initialize the Routing Table
        """

        self.routes = []


    def add_route(self, destination, next_hop, num_hops):
        """
        Add a new route to the routing table.

        Args:
            destination (int): The port number of the destination router
            next_hop (int): The port number of the next router in-sequence
            num_hops (int): The cost to reach the next router

        """

        route = routing_entry.RoutingEntry(destination, next_hop, num_hops)
        self.routes.append(route)
