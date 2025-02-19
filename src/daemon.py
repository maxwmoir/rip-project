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
import datetime
import calendar

# Local Imports
import packet
from packet import RIPPacket, RIPEntry

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
        
    print("Input Ports are Valid!")
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
        if not 1 <= metric <= 15:
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
        
    print("Output Ports are Valid!")
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

    def __init__ (self, id, config):
        """
        Initialize the Daemon.

        Args:
            id (int): The identifier for this Daemon
            config (str): The config file used to initialize the Daemon
        """

        # Initialise variables
        self.id = id
        self.config = config
        self.inputs = []
        self.outputs = []
        self.socks = []

        # Call methods
        self.read_config()
        self.print_info()
        self.bind_sockets()

        # ::DEBUG:: Print socket configuration
        for sock in self.socks:
            print(sock)

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
                if (len(line)):
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
                            port, metric, router_id = [[int(v) for v in l.decode().split("-")] for l in line[1:]]
                            self.outputs = [port, metric, router_id]
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

        for i in range(len(self.inputs)):
            print(f"Binding socket to port {self.inputs[i]}")

            # Create each socket
            try:
                self.socks.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
            except:
                for sock in self.socks:
                    if sock != None:
                        sock.close()
                print("ERROR: Socket creation failed")
                exit()

            # Bind each socket
            try:
                self.socks[i].bind(("localhost", self.inputs[i]))
            except:
                for sock in self.socks:
                    if sock != None:
                        sock.close()
                print("ERROR: Socket binding failed")
                exit()


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
    id = sys.argv[1]
    config = sys.argv[2]
    daemon = Daemon(id, config)

    ents = [
        RIPEntry(2, 3),
        RIPEntry(3, 6),
        RIPEntry(5, 5),
        RIPEntry(1, 2),
    ]

    a_packet = RIPPacket(packet.COMMAND_RESPONSE, 2, ents)
    
    encoded_packet = packet.encode_packet(a_packet)
    decoded_packet = packet.decode_packet(encoded_packet)

    print(a_packet)
    print(decoded_packet)
