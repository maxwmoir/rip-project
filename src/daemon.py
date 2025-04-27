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
RESPONSE_MESSAGE_INTERVAL = 30
RESPONSE_MESSAGE_RANGE = 5
ROUTE_TIMEOUT = 180
GARBAGE_COLLECTION_TIME = 120
CLEAR_TIMER_INTERVAL = 200
TIMER_DIVISOR = 100

# Potential states for routing daemon
class State():
    INIT = "INITIALISING"
    LISTENING = "LISTENING"
    PROCESSING_MESSAGE = "PROCESSING_MESSAGE"
    FLOODING = "FLOODING_NEIGHBOURS"
    UPDATING = "UPDATING_TABLE`"
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
        port, metric, peer_id = port_shell

        valid = verify_port_number(port)

        # Check metric validity
        if not 1 <= metric <= 500:
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

    def __init__ (self, config):
        """
        Initialize the Daemon.

        Args:
            id (int): The identifier for this Daemon
            config (str): The config file used to initialize the Daemon
        """

        # Initialise variables
        self.id = None
        self.config = config
        self.inputs = []
        self.outputs = []
        self.socks = []
        self.state = State.INIT
        self.table = RoutingTable()
        self.history = [] # For testing
        self.C = {}
        self.running = True

        # Initialise timers
        self.flood_timer = Timer()
        self.flood_interval = RESPONSE_MESSAGE_INTERVAL / TIMER_DIVISOR


        # TODO REmove these 
        self.timeout_length = ROUTE_TIMEOUT / TIMER_DIVISOR
        self.garbage_length = GARBAGE_COLLECTION_TIME / TIMER_DIVISOR
        self.update_timer = None
        self.naive_timer = None
        self.select_timeout = None
        self.clear_timer = None

        # Call methods
        self.read_config()
        self.bind_sockets()
        self.request_packet = RIPPacket(packet.COMMAND_REQUEST, self.id)

    def read_config(self):
        """
        Read the stored config file.
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
                                self.C[out[2]] = out[1]

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
                for sock in self.socks:
                    if sock is not None:
                        sock.close()
                print("ERROR: Socket creation failed")
                print(e)
                exit()

            # Bind each socket
            try:
                self.socks[i].bind((NETWORK_ADDRESS, port))
            except Exception as e:
                for sock in self.socks:
                    if sock is not None:
                        sock.close()
                print("ERROR: Socket binding failed")
                print(e)
                exit()



    def send_packet(self, pack, dest):
        """
        Send message to output port
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

            sock.settimeout(1.0)
            message = packet.encode_packet(pack)

            address = (address, port)
            try:
                sock.sendto(message, address)

            except Exception as e:
                print("ERROR: Sending failed")
                print(e)
                exit()
        finally:
            if sock is not None:
                sock.close()


    def flood_requests(self):
        """
        Flood all adjacent routers with request packets
        """
        for output in self.outputs:
            sock = None
            try:
                address =   NETWORK_ADDRESS 
                port = output[0]
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                except Exception as e:
                    print("ERROR: Socket creation failed")
                    print(e)
                    exit()

                sock.settimeout(1.0)
                message = packet.encode_packet(self.request_packet)
                address = (address, port)
                try:
                    sock.sendto(message, address)

                except Exception as e:
                    print("ERROR: Sending failed")
                    print(e)
                    exit()

            except Exception as error:
                print(f"ERROR: {error}")

            finally:
                if sock is not None:
                    sock.close()


    def handle_response(self, response):
        """
        Function to handle response event
        """
        inc_packet = packet.decode_packet(response)

        if inc_packet.command == 1:
            # If the incoming packet is a response packet, send routing table to the requesting router.
            entries = []

            # Split horizon with poisoned reverse
            for route in self.table.routes.values():
                if route.next_hop == inc_packet.from_router_id:
                    entries.append(RIPEntry(route.destination, 16))
                else:
                    entries.append(RIPEntry(route.destination, route.metric))

            # Send routing table to adjacent router
            response_packet = RIPPacket(packet.COMMAND_RESPONSE, self.id, entries)
            self.send_packet(response_packet, inc_packet.from_router_id)

        if inc_packet.command == 2:
            # If we recieve routing information from another router, update our database to include it. 
            for entry in inc_packet.entries:

                if entry.to_router_id in self.table.routes.keys():
                    # Handle route already in table

                    potential_metric = entry.metric + self.C[inc_packet.from_router_id]  
                    if potential_metric < self.table.routes[entry.to_router_id].metric:
                        # Replace current route with better metric
                        self.table.routes[entry.to_router_id].metric = entry.metric + self.C[inc_packet.from_router_id]
                        self.table.routes[entry.to_router_id].next_hop = inc_packet.from_router_id

                    if potential_metric == self.table.routes[entry.to_router_id].metric:
                        self.table.routes[entry.to_router_id].timeout_timer = time.time()
                        self.table.routes[entry.to_router_id].garbage_timer = 0.0

                else:
                    # Add new route to table 
                    if entry.metric + self.C[inc_packet.from_router_id] > 16:
                        self.table.add_route(entry.to_router_id, inc_packet.from_router_id, 16)
                    else:
                        self.table.add_route(entry.to_router_id, inc_packet.from_router_id, entry.metric + self.C[inc_packet.from_router_id])
                

    def handle_periodic_update(self):
        self.flood_requests()
        self.flood_timer.reset()
        self.flood_interval = random.randint(RESPONSE_MESSAGE_INTERVAL - RESPONSE_MESSAGE_RANGE, RESPONSE_MESSAGE_INTERVAL + RESPONSE_MESSAGE_RANGE) / TIMER_DIVISOR

    def update_table(self):
        to_delete = []
        for destination, route in self.table.routes.items():

            if route.destination != self.id:
                cur_time = time.time()
                # Check if timeout has occurred and mark as unreachable
                if cur_time - route.timeout_timer >= self.timeout_length and route.garbage_timer == 0.0:
                    route.metric = 16
                    # print(f"Route to {route.destination} timed out. Marking as unreachable.")

                # Start garbage collection
                if route.metric == 16 and not route.garbage_timer:
                    route.garbage_timer = time.time()
                    
                # Garbage collection time exceeded, mark for deletion
                if route.garbage_timer and cur_time - route.garbage_timer >= self.garbage_length:
                    to_delete.append(destination)

        # Now actually delete the routes
        for destination in to_delete:
            print(f"Deleting route to {destination} after garbage collection.")
            del self.table.routes[destination]


    def start(self):
        """
        Router mainloop
        """

        # Don't want it to do this eventually:
        self.table.add_route(self.id, self.id, 0)

        self.select_timeout = 0.1
        self.naive_timer = time.time()
        self.clear_timer = time.time()        
        self.state = State.LISTENING
        
        while self.state is State.LISTENING:
            self.update_table()

            if self.flood_timer.get_uptime() > self.flood_interval:
                self.handle_periodic_update()

            # Handle received packets
            readable_sockets, _, _ = select.select(self.socks, [], [], self.select_timeout)
            
            for sock in readable_sockets:
                if sock in self.socks:
                    try:
                        response, _ = sock.recvfrom(1024)
                        self.handle_response(response)

                    except Exception as e:
                        print(e)
                        for sock in self.socks:
                            if sock is not None:
                                sock.close()



    def __str__(self):
        return f"ID: {self.id}"

    def print_info(self):
        """
        Print information about the daemon to the console.
        """

        print("ID: ", self.id)
        print("conf: ", self.config)
        print("inputs: ", self.inputs)
        print("outputs: ", self.outputs)


# Run the program
if __name__ == "__main__":
    config_name = sys.argv[1]
    daemon = Daemon(config_name)
