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
        self.routes = {}

    def add_route(self, destination, next_hop, metric):
        """
        Add a new route to the routing table.

        Args:
            destination (int): The port number of the destination router
            next_hop (int): The port number of the next router in-sequence
            metric (int): The cost to reach the destination router 

        """

        route = routing_entry.RoutingEntry(destination, next_hop, metric)
        if destination not in self.routes.keys():
            self.routes[destination] = route
        
    def update_timers(self, age):
        """
        Update the age, timeout, and garbage timers of each routing entry.
        Delete entries after their garbage timers time out.
        """

        to_delete = []

        for destination, route in self.routes.items():
            route.age += age
            route.timeout_timer += age

            # Check if timeout has occurred and mark as unreachable
            if route.timeout_timer >= 180 and route.garbage_timer == 0.0:
                route.metric = 16
                route.garbage_timer = 0.0
                print(f"Route to {route.destination} timed out. Marking as unreachable.")

            # Start garbage collection
            if route.metric == 16:
                route.garbage_timer += age
                
                # Garbage collection time exceeded, mark for deletion
                if route.garbage_timer >= 120:
                    to_delete.append(destination)

        # Now actually delete the routes
        for destination in to_delete:
            print(f"Deleting route to {destination} after garbage collection.")
            del self.routes[destination]



    def print_table(self):
        """
        Prints out the routing table infomation
        """
        print("dest next num_hops")
        for route in self.routes.values():
            print(f"{route.destination}    {route.next_hop}    {route.metric}")
