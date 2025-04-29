"""
COSC364 - RIP Programming Assignment
- daemon.py

Created: 
- 18/02/25

Authors: 
- Martyn Gascoigne
- Max Moir
"""

# Package Imports
import socket
import sys
import select
import time
import random

# Local Imports
import packet
from packet import RIPPacket, RIPEntry
from routing_table import RoutingTable
from timer import Timer

# Constants
NETWORK_ADDRESS = 'localhost'
UPDATE_INTERVAL = 30
UPDATE_TIME_RANGE = 5
ROUTE_TIMEOUT = 180
GARBAGE_COLLECTION_TIME = 120
NUMBER_OF_ROUTERS = 7
TIMER_DIVISOR = 1000


class State():
    """
    Class to store the set of possible routing daemon states.
    """
    INIT = "INITIALISING"
    LISTENING = "LISTENING"
    DISABLED  = "DISABLED"
    SHUT_DOWN = "SHUT_DOWN"


def verify_input_ports(input_ports):
    """
    Helper method to check validity of the input port numbers.

    Args:
        input_ports (list::int): The ports to check

    Returns:
        Boolean indicating success
    """

    seen_ports = set()

    # Loop and "check off" seen ports whilst also verifying them
    for port in input_ports:
        valid = verify_port_number(port)

        # Check if port is a duplicate
        if port in seen_ports:
            valid = False
        else:
            seen_ports.add(port)

        # Something went wrong and these ports are invalid!
        if not valid:
            print("ERROR: 1 or more Input Ports are Invalid!")
            return False

    # print("Input Ports are Valid!")
    return True


def verify_output_ports(input_ports, output_ports):
    """
    Helper method to check validity of the output port numbers.

    Args:
        input_ports (list::int): The input ports to check
        output_ports (list::int): The output ports to check

    Returns:
        Boolean indicating success
    """

    seen_ports = set()

    # Loop and "check off" seen ports whilst also verifying them
    for port_shell in output_ports:
        port, metric, _ = port_shell

        valid = verify_port_number(port)

        # Check metric validity
        if not 1 <= metric <= 16:
            valid = False

        # Check if port is a duplicate
        if port in seen_ports:
            valid = False
        else:
            seen_ports.add(port)

        # Check if port is also an input
        if port in input_ports:
            valid = False

        # Something went wrong and these ports are invalid!
        if not valid:
            print("ERROR: 1 or more Output Ports are Invalid!")
            return False

    # print("Output Ports are Valid!")
    return True


def verify_port_number(port_number):
    """
    Helper method to check validity of a given port number.

    Args:
        port_number (int): The port to check

    Returns:
        Boolean indicating success
    """

    return 1024 <= port_number <= 64000


class Daemon():
    """
    Class implementing the router daemon.
    """

    def __init__ (self, config, print_verbose = False):
        """
        Initialize the Daemon.

        Args:
            id (int): The identifier for this Daemon
            config (str): The config file used to initialize the Daemon
        """

        # Initialise variables
        self.id = None
        self.config = config
        self.verbose = print_verbose
        self.inputs = []
        self.outputs = []
        self.socks = []
        self.state = State.INIT
        self.table = RoutingTable()
        self.adjacent_metrics = {}
        self.running = True

        # Initialise Timers
        self.periodic_timer = Timer()
        self.print_timer = Timer()

        # Initialise Timeouts
        self.periodic_update_interval = UPDATE_INTERVAL / TIMER_DIVISOR
        self.select_timeout = 0.1
        self.timeout_length = ROUTE_TIMEOUT / TIMER_DIVISOR
        self.garbage_length = GARBAGE_COLLECTION_TIME / TIMER_DIVISOR

        # Call startup methods
        self.read_config()
        self.bind_sockets()


    def read_config(self):
        """
        Read the configuration file and set up the router.
        """

        try:
            f = open(self.config, "rb")
        except OSError:
            print ("Could not read file")
            exit()

        # Read File
        with f:
            lines = f.readlines()

            contains_router_id = False
            contains_input_ports = False
            contains_output_ports = False

            for line in [l.split() for l in lines]:
                if len(line):
                    match line[0]:
                        case b"router-id":
                            self.id = int(line[1])
                            contains_router_id = True

                        case b"input-ports":
                            # Convert input ports
                            self.inputs = [int(l) for l in line[1:]]
                            contains_input_ports = True

                            verify_input_ports(self.inputs)

                        case b"output-ports":
                            # Convert Port Number, Metric Value and Peer-Router ID into integers
                            outs = [[int(v) for v in l.decode().split("-")] for l in line[1:]]

                            for out in outs:
                                self.adjacent_metrics[out[2]] = out[1]

                            self.outputs = outs
                            contains_output_ports = True

                            verify_output_ports(self.inputs, self.outputs)

            # Ensure all config parameters exist in the config file
            if not (contains_router_id and contains_input_ports and contains_output_ports):
                print("ERROR: Config File is missing Parameters!")
                exit()


    def bind_sockets(self):
        """
        Bind the appropriate UDP sockets.
        """

        for i, port in enumerate(self.inputs):
            # Create each socket
            try:
                self.socks.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
            except Exception as e:
                self.shut_down()
                print("ERROR: Socket creation failed")
                print(e)
                exit()

            # Bind each socket
            try:
                self.socks[i].bind((NETWORK_ADDRESS, port))
            except Exception as e:
                self.shut_down()
                print("ERROR: Socket binding failed")
                print(e)
                exit()

    def send_packet(self, pack, dest):
        """
        Send a packet to the specified destination.

        Args:
            pack (RIPPacket): The packet to send
            dest (int): The destination router ID
        """

        output = None
        for o in self.outputs:
            if o[2] == dest:
                output = o

        if not output:
            return

        try:
            address = NETWORK_ADDRESS
            port = output[0]
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except Exception as e:
                print("ERROR: Socket creation failed")
                print(e)
                exit()

            # Socket options
            sock.settimeout(1.0)
            message = packet.encode_packet(pack)

            # Attempt to send the packet
            address = (address, port)
            try:
                sock.sendto(message, address)
            except Exception as e:
                print("ERROR: Sending failed")
                print(e)
                exit()
        finally:
            # Close the socket after the packet has been sent
            # or if an error occurred
            if sock is not None:
                sock.close()


    def update_neighbours(self):
        """
        Flood all adjacent routers with routing table.
        """

        for output in self.outputs:
            entries = []

            # Split horizon with poisoned reverse
            for route in self.table.routes.values():
                if route.destination is not output[2]:
                    if route.next_hop == output[2]:
                        entries.append(RIPEntry(route.destination, 16))
                    else:
                        entries.append(RIPEntry(route.destination, route.metric))

            # Send routing table to adjacent router
            response_packet = RIPPacket(packet.COMMAND_RESPONSE, self.id, entries)
            self.send_packet(response_packet, output[2])


    def handle_response(self, response):
        """
        Handle incoming packets from the socket.

        Args:
            response (bytearray): The packet received from the socket
        """

        inc_packet = packet.decode_packet(response)

        if inc_packet.command == packet.COMMAND_RESPONSE:

            # Add route of adjacent router to the routing table
            if inc_packet.from_router_id not in self.table.routes.keys():
                metric = self.adjacent_metrics[inc_packet.from_router_id]
                self.table.add_route(inc_packet.from_router_id, inc_packet.from_router_id, metric)
            else:
                # If route is already in routing table then update its metric
                metric = self.adjacent_metrics[inc_packet.from_router_id]
                self.table.routes[inc_packet.from_router_id].metric = metric
                self.table.routes[inc_packet.from_router_id].next_hop = inc_packet.from_router_id

                # In addition, reset its timers
                self.table.routes[inc_packet.from_router_id].timeout_timer = time.time()
                self.table.routes[inc_packet.from_router_id].garbage_timer = 0.0

            # If we recieve routing information from another router, update database to include it.
            for entry in inc_packet.entries:

                # Handle route already in table
                if entry.to_router_id in self.table.routes.keys():

                    # Potential metric
                    pot_metric = entry.metric + self.adjacent_metrics[inc_packet.from_router_id]

                    # Replace current route with better metric
                    if pot_metric < self.table.routes[entry.to_router_id].metric:
                        metric = entry.metric + self.adjacent_metrics[inc_packet.from_router_id]
                        self.table.routes[entry.to_router_id].metric = metric
                        self.table.routes[entry.to_router_id].next_hop = inc_packet.from_router_id

                        # Reset route timeout_timer after an update
                        self.table.routes[entry.to_router_id].timeout_timer = time.time()
                        self.table.routes[entry.to_router_id].garbage_timer = 0.0

                    # Reset timeout if metric is the same
                    if pot_metric == self.table.routes[entry.to_router_id].metric:
                        self.table.routes[entry.to_router_id].timeout_timer = time.time()
                        self.table.routes[entry.to_router_id].garbage_timer = 0.0
                else:
                    # Add new route to table
                    if entry.metric + self.adjacent_metrics[inc_packet.from_router_id] <= 16:
                        metric = entry.metric + self.adjacent_metrics[inc_packet.from_router_id]
                        self.table.add_route(entry.to_router_id, inc_packet.from_router_id, metric)

    def update_table(self):
        """
        Update the routing table by checking for timeouts and garbage collection.
        """

        to_delete = []
        for destination, route in self.table.routes.items():

            if route.destination != self.id:
                t_cur = time.time()
                # Check if timeout has occurred and mark as unreachable
                if t_cur - route.timeout_timer >= self.timeout_length and not route.garbage_timer:
                    route.metric = 16
                    if self.verbose:
                        print(f"R{self.id} - Route to R{route.destination} timed out.")

                # Start garbage collection
                if route.metric == 16 and not route.garbage_timer:
                    route.garbage_timer = time.time()

                    # Send a triggered update
                    self.update_neighbours()

                # Garbage collection time exceeded, mark for deletion
                if route.garbage_timer and t_cur - route.garbage_timer >= self.garbage_length:
                    to_delete.append(destination)

        # Now actually delete the routes
        for destination in to_delete:
            if self.verbose:
                print(f"R{self.id} - Deleting route to R{destination} after garbage collection.")
            del self.table.routes[destination]


    def handle_periodic_update(self):
        """
        Periodically update all adjacent routers with routing table.
        """

        self.update_table()
        self.update_neighbours()
        self.periodic_timer.reset()

        # Choose random interval to avoid router update collisions
        lower_bound = UPDATE_INTERVAL - UPDATE_TIME_RANGE
        upper_bound = UPDATE_INTERVAL + UPDATE_TIME_RANGE
        self.periodic_update_interval = random.randint(lower_bound, upper_bound) / TIMER_DIVISOR


    def handle_print_table(self):
        """
        Print the routing table table and reset the print table timer.
        """

        self.print_table()
        self.print_timer.reset()


    def start(self):
        """
        Start the routing daemon and begin listening for incoming packets.
        """

        self.print_timer.start()
        self.state = State.LISTENING

        while self.state is State.LISTENING:
            if self.periodic_timer.get_uptime() > self.periodic_update_interval:
                self.handle_periodic_update()

            if self.print_timer.get_uptime() > 3:
                self.handle_print_table()

            # Handle received packets
            readable_sockets, _, _ = select.select(self.socks, [], [], self.select_timeout)

            for sock in readable_sockets:
                if sock in self.socks:
                    try:
                        response, _ = sock.recvfrom(1024)
                        self.handle_response(response)

                    except Exception as e:
                        print(e)
                        self.shut_down()

    def disable(self):
        """
        Disable the daemon.
        """

        if self.state == State.LISTENING:
            self.state = State.DISABLED
            time.sleep(0.1)
            self.table = RoutingTable()

    def shut_down(self):
        """
        Shut down the daemon.
        """

        if self.state is not State.SHUT_DOWN:
            self.state = State.SHUT_DOWN
            time.sleep(0.1)
            for sock in self.socks:
                if sock is not None:
                    sock.close()

    def print_table(self):
        """
        Print routing table to console.
        """

        print(f"+--------------------- Router {self.id:02} ----------------------+")
        print( "| dest   next_hop     metric    timeout   garbage_time |")

        for i in range(NUMBER_OF_ROUTERS):
            if i + 1 in self.table.routes.keys():
                route = self.table.routes[i + 1]
                print(f"|{route.destination:5} {route.next_hop:10} {route.metric:10} {(time.time() - route.timeout_timer):10.3g} {route.garbage_timer:14.3g} |")
            else:
                print(f"|    {i + 1}          -          -          -              - |")
        print("+------------------------------------------------------+")


    def __del__(self):
        """
        Handle daemnon deletion.
        """

        self.shut_down()


    def __str__(self):
        """
        String representation of the Daemon object.
        """

        return f"Daemon Object: Daemon ID: {self.id}"


# Handle daemon creation from the command line.
if __name__ == "__main__":

    config_name = sys.argv[1]

    verbose = False
    if len(sys.argv) > 2 and sys.argv[2] == "-v":
        verbose = True

    daemon = Daemon(config_name, verbose)

    try:
        daemon.start()
    finally:
        daemon.shut_down()
