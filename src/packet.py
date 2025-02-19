"""
COSC364 - RIP Programming Assignment
- packet.py

Created: 
- 18/02/25

Authors: 
- Martyn Gascoigne
- Max Moir
"""

import struct
import socket

"""
Class for storing data to be sent / received by the router.
"""
class RIPPacket():
    COMMAND_REQUEST = 1
    COMMAND_RESPONSE = 2
    VERSION = 2
    AFI = 2 # Address Family Identifier

    """
    Initialise the packet object.
    """
    def __init__(self, command, from_router_id, entries=[]):
        self.command = command
        self.version = self.VERSION
        self.from_router_id = from_router_id
        self.entries = entries

    def add_entry(self, to_router_id, metric, afi=AFI):
        self.entries.append(RIPEntry(afi, to_router_id, metric))


"""
Class for storing a single entry to be delivered in a packet.
"""
class RIPEntry():
    def __init__(self, afi, to_router_id, metric):
        self.afi = afi
        self.to_router_id = to_router_id
        self.metric = metric