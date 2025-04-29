"""
COSC364 - RIP Programming Assignment
- packet.py

Created: 
- 18/02/25

Authors: 
- Martyn Gascoigne
- Max Moir
"""

# Constants for the RIP protocol
COMMAND_REQUEST = 1
COMMAND_RESPONSE = 2
VERSION = 2
AFI = 2

class RIPPacket():
    """
    Class for storing data to be sent / received by the router.
    """

    def __init__(self, command, from_router_id, entries=None):
        """
        Initialise the RIP packet object.
        Runs a simple validation check to ensure the packet is valid.

        Args:
            command (int): The ID of the command
            from_router_id (int): The ID of the router this packet is being sent from
            entries (list::RIPEntry): The cost to reach the next router
        """
        try:
            self.validate_initialisation(command, from_router_id, entries)
        except ValueError as e:
            print(f"Failed to initialise packet")
            print(e)
            raise e

        # Initialise the packet object
        self.command = command
        self.version = VERSION
        self.from_router_id = from_router_id
        self.entries = entries if entries else []

    def validate_initialisation(self, command, from_router_id, entries):
        """
        Validate the initialisation of the RIP packet object.
        Args:
            command (int): The ID of the command
            from_router_id (int): The ID of the router this packet is being sent from
            entries (list::RIPEntry): The cost to reach the next router

        Raises:
            ValueError: If the command is not COMMAND_REQUEST(1) or COMMAND_RESPONSE(2),
                        if the router ID is not between 0 and 65535, 
                        if the entiries contain invalid router IDs or AFI values.

        Returns:
            bool: True if the initialisation is valid.
        """

        if command != COMMAND_REQUEST and command != COMMAND_RESPONSE:
            raise ValueError("Invalid command type. Must be 1 (request) or 2 (response).")
        if from_router_id < 0 or from_router_id > 65535:
            raise ValueError("Invalid router ID. Must be between 0 and 65535.")
        
        if entries:
            for entry in entries:
                if entry.to_router_id < 0 or entry.to_router_id > 65535:
                    raise ValueError("Invalid router ID. Must be between 0 and 65535.")
                if entry.afi != AFI:
                    raise ValueError("Invalid AFI. Must be 2 (IPv4).")
                if entry.metric < 1 or entry.metric > 16:
                    raise ValueError("Invalid metric. Must be between 0 and 16.")
        
        return True


    def add_entry(self, to_router_id, metric, afi=AFI):
        """
        Add a RIPEntry to this packet.

        Args:
            to_router_id (int): The ID of the router this packet is being sent frotom
            metric (int): The current metric for the destination
            afi (int): The Address Family Identifier of the entry
        """

        self.entries.append(RIPEntry(to_router_id, metric, afi))

    def __str__(self):
        """
        String representation of the packet object.
        """

        entries = f"{''.join([f"[To-ID: {l.to_router_id}, Metric: {l.metric}, AFI: {l.afi}], " for l in self.entries])}"
        return f"Packet-Object: Command Type: {self.command}, Version: {self.version}, From-ID: {self.from_router_id}, Entries: [{entries}]"


def encode_packet(input_packet):
    """
    Construct an encoded packet represented by a byte-array.

    Args:
        input_packet (RIPPacket): The packet to encode into a byte-array

    Returns:
        Encoded packet
    """

    header_size = 4
    payload_size = 20
    packet_size = header_size + payload_size * len(input_packet.entries)
    packet = bytearray(packet_size)

    # Form Header
    packet[0] = input_packet.command
    packet[1] = input_packet.version
    packet[2] = (input_packet.from_router_id >> 8) & 0xFF 
    packet[3] = (input_packet.from_router_id >> 0) & 0xFF

    # Store encoded entries
    for i, entry in enumerate(input_packet.entries):
        offset = payload_size * i

        packet[header_size + offset + 0]    = (entry.afi >> 8) & 0xFF
        packet[header_size + offset + 1]    = (entry.afi >> 0) & 0xFF
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


def decode_packet(encoded_packet):
    """
    Decode byte-array into a RIPPacket object that is usable by the router.

    Args:
        encoded_packet (bytearray): The packet to decode

    Returns:
        Decoded packet
    """

    header_size = 4
    payload_size = 20

    entries = []
    for i in range(header_size, len(encoded_packet), payload_size):
        afi = encoded_packet[i] << 8 | encoded_packet[i + 1]
        # must-be-zero segment
        to_router_id = encoded_packet[i + 4] << 24 | encoded_packet[i + 5] << 16 | encoded_packet[i + 6] << 8 | encoded_packet[i + 7]

        # must-be-zero segment
        metric = encoded_packet[i + 16] << 24 | encoded_packet[i + 17] << 16 | encoded_packet[i + 18] << 8 | encoded_packet[i + 19]

        entry = RIPEntry(to_router_id, metric, afi)
        entries.append(entry)

    # Form Header
    command = encoded_packet[0]
    # version = encoded_packet[1]
    from_router_id = encoded_packet[2] << 8 | encoded_packet[3]

    packet = RIPPacket(command, from_router_id, entries)

    # Return usable Packet
    return packet


class RIPEntry():
    """
    Class for storing a single entry to be delivered in a packet.
    """

    def __init__(self, to_router_id, metric, afi=AFI):
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
