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

"""
Class for storing all of the routing information for a router.
"""
class RoutingTable(): 
    def __init__(self):
        self.routes = []

    """
    Add a new route to the routing table.

    Args:
        destination (int): The port number of the destination router
        next_hop (int): The port number of the next router in-sequence
        num_hops (int): The cost to reach the next router

    """
    def add_route(self, destination, next_hop, num_hops):
        route = routing_entry.RoutingEntry(destination, next_hop, num_hops)
        self.routes.append(route)
        
