"""Contains code, related to ESPNow packet handling."""

# Maximum length of a packet in bytes
# (255 or 256 characters will lead to errors)
MAX_PACKET_LENGTH = 217


def index_or_false(packet, byte):
    """If there's a byte in bytearray, tells its first position.
    Otherwise returns False."""
    index = False
    if not isinstance(packet, (bytes, bytearray)):
        raise ValueError('Wrong packet type.')
    if not isinstance(byte, (bytes, bytearray)):
        raise ValueError('Wrong byte argument type.')
    if len(byte) > 1:
        raise ValueError('Wrong byte length, check input and type.')
    try:
        index = packet.index(byte)
    except ValueError:
        pass
    return index


def extract_message(packet, number_end_id, finished):
    """Extracts message from a packet."""
    message = False
    if finished:
        message = packet[number_end_id:finished - 1]
    else:
        message = packet[number_end_id + 1:]
    return message


def parse(packet, mac):
    """Parse ESPNow packet, tell to clear the whole message or extend it
    with new data."""
    # Throw an exception if our message and mac is not bytes
    if not isinstance(packet, (bytes, bytearray)):
        raise ValueError('Packet should be a bytearray.')
    if not isinstance(mac, (bytes, bytearray)):
        raise ValueError('MAC address should be bytearray.')
    # Throw an error if our message doesn't start with \x01
    if packet[0] != 1:
        raise ValueError('Message does not start with \x01.')
    topic_end_byte_id = index_or_false(packet, b'\x06')
    if topic_end_byte_id is False:
        raise ValueError('Wrong packet format, topic_end_byte_id not found.')
    number_end_id = index_or_false(packet, b'\x02')
    if number_end_id is False:
        raise ValueError('Wrong packet format, number_end_id not found.')
    topic = packet[1:topic_end_byte_id]
    # Parse packet number
    try:
        number = int(packet[topic_end_byte_id+1:number_end_id], 10)
    except ValueError:
        raise ValueError('Unable to parse packet number sector.')
    # Check if this packet is the last one in the message
    finished = index_or_false(packet, b'\x04')
    finished = (finished == len(packet) - 1)
    # Extract actual message from the packet
    message = extract_message(packet, number_end_id, finished)
    # If message format is wrong, but it contains a name,
    # we tell to remove the name.
    # Otherwise, we are appending yet another part of our message
    # to the stored value and parse it.
    result = {
        'topic': topic,
        'mac': mac,
        'finished': finished,
        'message': message,
        'number': number
    }
    return result


def gen_packet_header(topic, packet_id):
    """Generates a header for a given packet"""
    return b'\x01' + topic + \
           b'\x06' + str(packet_id).encode('ascii') + \
           b'\x02'


def split_to_packets(topic, message):
    """Splits bytes-typed message to several parts."""
    if not isinstance(topic, (bytes, bytearray)):
        raise ValueError('Topic should be a byte array.')
    if not isinstance(message, (bytes, bytearray)):
        raise ValueError('Message should be a byte array.')
    packet_id = 0
    tmp = message
    packet_list = []
    # Splitting the message to parts
    while tmp:
        header = gen_packet_header(topic, packet_id)
        split_len = MAX_PACKET_LENGTH - len(header)
        packet_list.append(header + tmp[:split_len])
        tmp = tmp[split_len:]
        packet_id += 1
    # Adding a closing packet
    header = gen_packet_header(topic, packet_id)
    packet_list.append(header + b'\x04')
    return packet_list
