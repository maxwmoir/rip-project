from src.packet import RIPPacket, RIPEntry, encode_packet, decode_packet, COMMAND_REQUEST, COMMAND_RESPONSE, VERSION
import pytest

def test_empty_packet_encoding():
    """
    Test encoding and decoding of an empty RIPPacket (no entries).
    """
    packet = RIPPacket(command=COMMAND_REQUEST, from_router_id=123)
    encoded = encode_packet(packet)
    decoded = decode_packet(encoded)

    assert decoded.command == COMMAND_REQUEST
    assert decoded.version == VERSION
    assert decoded.from_router_id == 123
    assert len(decoded.entries) == 0

def test_invalid_command():
    """
    Test that an invalid command raises an error or behaves as expected.
    """
    with pytest.raises(ValueError):
        RIPPacket(command=99, from_router_id=123)  # Assuming command 99 is invalid

def test_large_router_id():
    """
    Test encoding and decoding with a large router ID.
    """
    
    packet = RIPPacket(command=COMMAND_RESPONSE, from_router_id=65535)
    packet.add_entry(to_router_id=500, metric=10)
    encoded = encode_packet(packet)
    decoded = decode_packet(encoded)

    assert decoded.from_router_id == 65535
    assert decoded.entries[0].to_router_id == 500
    assert decoded.entries[0].metric == 10

def test_maximum_metric():
    """
    Test encoding and decoding with the maximum metric value.
    """

    packet = RIPPacket(command=COMMAND_RESPONSE, from_router_id=1)
    packet.add_entry(to_router_id=2, metric=16)  # RIP metric max is 16
    encoded = encode_packet(packet)
    decoded = decode_packet(encoded)

    assert decoded.entries[0].metric == 16

def test_multiple_packets():
    """
    Test encoding and decoding of multiple packets to ensure no interference.
    """

    packet1 = RIPPacket(command=COMMAND_REQUEST, from_router_id=1)
    packet1.add_entry(to_router_id=2, metric=5)

    packet2 = RIPPacket(command=COMMAND_RESPONSE, from_router_id=3)
    packet2.add_entry(to_router_id=4, metric=10)

    encoded1 = encode_packet(packet1)
    encoded2 = encode_packet(packet2)

    decoded1 = decode_packet(encoded1)
    decoded2 = decode_packet(encoded2)

    assert decoded1.from_router_id == 1
    assert decoded1.entries[0].to_router_id == 2
    assert decoded1.entries[0].metric == 5

    assert decoded2.from_router_id == 3
    assert decoded2.entries[0].to_router_id == 4
    assert decoded2.entries[0].metric == 10

def test_multiple_entries():
    """
    Test encoding and decoding of a packet with multiple entries.
    """

    packet = RIPPacket(command=2, from_router_id=500)
    packet.add_entry(to_router_id=600, metric=20)
    packet.add_entry(to_router_id=700, metric=25)
    encoded = encode_packet(packet)
    decoded = decode_packet(encoded)

    assert len(decoded.entries) == 2
    assert decoded.entries[0].to_router_id == 600
    assert decoded.entries[0].metric == 20
    assert decoded.entries[1].to_router_id == 700
    assert decoded.entries[1].metric == 25