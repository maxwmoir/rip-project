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
    Initialise the RIP packet object.

    Args:
        command (int): The ID of the command
        from_router_id (int): The ID of the router this packet is being sent from
        entries (list::RIPEntry): The cost to reach the next router
    """
    def __init__(self, command, from_router_id, entries=[]):
        self.command = command
        self.version = self.VERSION
        self.from_router_id = from_router_id
        self.entries = entries

    """
    Add a RIPEntry to this packet.

    Args:
        to_router_id (int): The ID of the router this packet is being sent frotom
        metric (int): The current metric for the destination
        afi (int): The Address Family Identifier of the entry
    """
    def add_entry(self, to_router_id, metric, afi=AFI):
        self.entries.append(RIPEntry(afi, to_router_id, metric))


"""
Class for storing a single entry to be delivered in a packet.
"""
class RIPEntry():
    """
    Initialise the RIP entry object.

    Args:
        to_router_id (int): The ID of the router this packet is being sent frotom
        metric (int): The current metric for the destination
        afi (int): The Address Family Identifier of the entry
    """
    def __init__(self, to_router_id, metric, afi):
        self.to_router_id = to_router_id
        self.metric = metric
        self.afi = afi