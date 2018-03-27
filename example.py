# Send data
from wrapper import ESPNowHandler
from wrapper import TestTopicEndpoint
tte = TestTopicEndpoint()
handler = ESPNowHandler()
espnow_bcast = b'\xFF' * 6
handler.bind_endpoint(b'test topic', tte)
tte.send(espnow_bcast, b'test msg')
handler.step()

# Receive data
from wrapper import ESPNowHandler
from wrapper import TestTopicEndpoint
tte = TestTopicEndpoint()
handler = ESPNowHandler()
espnow_bcast = b'\xFF' * 6
handler.bind_endpoint(b'test topic', tte)
handler.step()

# Asynchronous processing
import uasyncio as asyncio
from wrapper import ESPNowHandler
from wrapper import TestTopicEndpoint

tte = TestTopicEndpoint()
handler = ESPNowHandler()
espnow_bcast = b'\xFF' * 6

async def espnow_step():
    while True:
        handler.step()
        asyncio.sleep(0.1)

handler.bind_endpoint(b'test topic', tte)
handler.step()

loop = asyncio.get_event_loop()
loop.run_until_complete(espnow_step())
