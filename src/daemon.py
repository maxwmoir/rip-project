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

"""
Class implementing the router daemon.
"""
class Daemon():

    """
    Initialize the Daemon.
    """
    def __init__ (self, id, config):
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

    """
    Read the stored config file.
    """
    def read_config(self):
        try:
            f = open(self.config, 'rb')
        except OSERROR:
            print ("Could not read file")
            sys.exit()
        with f:
            lines = f.readlines()

            for line in [l.split() for l in lines]:
                if (len(line)):
                    match line[0]:
                        case b'router-id':
                            self.id = int(line[1])
                        case b'input-ports':
                            self.inputs = [int(l) for l in line[1:]]
                        case b'output-ports':
                            self.outputs = [int(l) for l in line[1:]]

    """
    Bind the appropriate UDP sockets.
    """
    def bind_sockets(self):
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

    """
    Print information about the daemon to the console.
    """
    def print_info(self):
        print("ID: ", self.id)
        print("conf: ", self.config)
        print("inputs: ", self.inputs)
        print("outputs: ", self.outputs)

# Run the program
if __name__ == '__main__':
    id = sys.argv[1]
    config = sys.argv[2]
    daemon = Daemon(id, config)
