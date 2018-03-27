from esp import espnow
from packet import parse, split_to_packets
from buffer import CommunicationBuffer
from network import WLAN, MODE_LR


class ESPNowHandler(object):
    """Receives ESPNow packets, stores to a buffer,
    passes closed buffers to a finished callback."""

    def __init__(self):
        # Store buffer and endpoints in RAM
        self.buffer = CommunicationBuffer()
        self.endpoints = {}
        # Init network
        self.wlan = WLAN()
        self.wlan.active(True)
        self.wlan.config(protocol=MODE_LR)
        # Init ESPNow
        espnow.init()

    def push_packet(self, mac, packet):
        """Passes packet to internal packet handler."""
        packet_processing_result = parse(packet, mac)
        self.buffer.push(packet_processing_result)

    def send_message(self, topic, message, mac):
        """Sends a message with a given topic to a given MAC."""
        # Adds a peer if it doesn't exist
        if not espnow.peer_exists(mac):
            espnow.add_peer(self.wlan, mac)
        # Packets to send
        packets = split_to_packets(topic, message)
        # Send packets to a given MAC
        for packet in packets:
            espnow.send(mac, packet)

    def bind_endpoint(self, topic, endpoint):
        """Binds an endpoint to current handler."""
        endpoint.bind(topic, self)
        self.endpoints[topic] = endpoint

    def step(self):
        """Checks if there are complete buffers, pops one,
           passes it to an appropriate handler object / function."""
        # Store data in a buffer
        if espnow.data_available():
            mac = espnow.extract_mac_list()
            if mac:
                mac = mac[0]
                packets = espnow.extract_list_by_mac(mac)
                for packet in packets:
                    self.push_packet(mac, packet)
        # Send available messages from the buffer
        # to an appropriate handler
        handler_message = self.buffer.pop()
        if handler_message != False:
            print(handler_message)
            topic = handler_message['topic']
            self.endpoints[topic].process_input(
                handler_message['mac'],
                handler_message['data']
            )


class TestTopicEndpoint(object):
    """TODO"""

    def __init__(self):
        self.handler_topic = None
        self.handler = None

    def bind(self, handler_topic, handler):
        """Sets a parent handler and stores a topic"""
        self.handler_topic = handler_topic
        self.handler = handler

    def process_input(self, mac, data):
        """Handles data input"""
        message = """Test topic endpoint received input data.\n
        MAC: {}
        DATA: {}
        """
        print(message.format(mac, data))
        del mac
        del data

    def send(self, mac, message):
        """TODO"""
        self.handler.send_message(self.handler_topic, message, mac)

#
# if __name__ == '__main__':
#     pass
