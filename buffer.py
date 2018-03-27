class CommunicationBuffer(object):
    """Communication buffer handles packet streams
    from each MAC. It allows to extract finished messages
    with mac addresses."""

    def __init__(self):
        self.buffers = {}
        self.buffer_ids = {}
        self.closed_buffers = []

    def remove_topic_buffer(self, mac, topic):
        """Removes a topic buffer, its id,
        removes buffer dict for a given MAC."""
        del self.buffers[mac][topic]
        del self.buffer_ids[mac][topic]
        # Further cleanup
        if len(self.buffers[mac]) is 0:
            del self.buffers[mac]
            del self.buffer_ids[mac]

    def push(self, packet):
        """Stores a packet, builds messages."""
        number, mac, topic, finished = packet['number'], \
            packet['mac'], packet['topic'], \
            packet['finished']
        if mac not in self.buffers:
            self.buffers[mac] = {}
            self.buffer_ids[mac] = {}
        if topic not in self.buffers[mac]:
            self.buffer_ids[mac][topic] = 0
            self.buffers[mac][topic] = b''
        else:
            self.buffer_ids[mac][topic] += 1
        # If our buffer packet id matches updated one,
        # we update buffer, otherwise, it will be removed.
        if self.buffer_ids[mac][topic] == number:
            self.buffers[mac][topic] += packet['message']
        else:
            self.remove_topic_buffer(mac, topic)
        if finished is True:
            self.closed_buffers.append({
                'mac': mac,
                'topic': topic,
                'data': self.buffers[mac][topic],
            })
            self.remove_topic_buffer(mac, topic)

    def closed_buffer_available(self):
        """Returns true if we have
        some finished messages to process."""
        return len(self.closed_buffers) > 0

    def pop(self):
        """Returns one available buffer or returns False."""
        result = False
        if self.closed_buffer_available():
            result = self.closed_buffers.pop()
        return result