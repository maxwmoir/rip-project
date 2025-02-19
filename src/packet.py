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


class RIPPacket():
    """
    Class for storing data to be sent / received by the router.
    """
    
    COMMAND_REQUEST = 1
    COMMAND_RESPONSE = 2
    VERSION = 2
    AFI = 2 # Address Family Identifier

    def __init__(self, command, from_router_id, entries=[]):
        """
        Initialise the RIP packet object.

        Args:
            command (int): The ID of the command
            from_router_id (int): The ID of the router this packet is being sent from
            entries (list::RIPEntry): The cost to reach the next router
        """

        self.command = command
        self.version = self.VERSION
        self.from_router_id = from_router_id
        self.entries = entries


    def add_entry(self, to_router_id, metric, afi=AFI):
        """
        Add a RIPEntry to this packet.

        Args:
            to_router_id (int): The ID of the router this packet is being sent frotom
            metric (int): The current metric for the destination
            afi (int): The Address Family Identifier of the entry
        """

        self.entries.append(RIPEntry(afi, to_router_id, metric))

    def encode_packet(self):
        """
        Construct an encoded packet represented by a byte-array.

        Returns:
            Encoded packet
        """

        header_size = 4
        payload_size = 20
        packet_size = header_size + payload_size * len(self.entries)
        packet = bytearray(packet_size)

        # Form Header
        packet[0] = self.command
        packet[1] = self.version
        packet[2] = (self.from_router_id >> 8) & 0xFF # shift right >> 8 and bitmask the initial byte (which is now the original leftmost byte)
        packet[3] = (self.from_router_id >> 0) & 0xFF # bitmask the initial byte as we have already collected the 2nd byte.
        
        # Store encoded entries
        for i in range(len(entries), 1):
            offset = payload_size * i
            entry = entries[i]

            packet[header_size + offset + 0]    = (entry.afi >> 8) & 0xFF # shift right >> 8 and bitmask the initial byte (which is now the original leftmost byte)
            packet[header_size + offset + 1]    = (entry.afi >> 0) & 0xFF # bitmask the initial byte as we have already collected the 2nd byte.
            # must-be-zero segment
            packet[header_size + offset + 4]    = (entry.to_router_id >> 24) & 0xFF # To-Router ID
            packet[header_size + offset + 5]    = (entry.to_router_id >> 16) & 0xFF # To-Router ID
            packet[header_size + offset + 6]    = (entry.to_router_id >> 8) & 0xFF # To-Router ID
            packet[header_size + offset + 7]    = (entry.to_router_id >> 0) & 0xFF # To-Router ID
            # must-be-zero segment
            packet[header_size + offset + 16]    = (entry.metric >> 24) & 0xFF # Metric
            packet[header_size + offset + 17]    = (entry.metric >> 16) & 0xFF # Metric
            packet[header_size + offset + 18]    = (entry.metric >> 8) & 0xFF # Metric
            packet[header_size + offset + 19]    = (entry.metric >> 0) & 0xFF # Metric
        
        # Return usable Packet
        return packet


    def decode_packet(self):
        pass


class RIPEntry():
    """
    Class for storing a single entry to be delivered in a packet.
    """


    def __init__(self, to_router_id, metric, afi):
        """
        Initialise the RIP entry object.

        Args:
            to_router_id (int): The ID of the router this packet is being sent frotom
            metric (int): The current metric for the destination
            afi (int): The Address Family Identifier of the entry
        """

        self.to_router_id = to_router_id
        self.metric = metric
        self.afi = afi