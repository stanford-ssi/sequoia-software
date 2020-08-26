import asyncio
import random


class Radio:
    def __init__(self):
        self.__queue_in = asyncio.Queue()
        self.__queue_out = asyncio.Queue()

    async def send_message(self, message):
        await asyncio.sleep(0.1)
        print(f"Sending Message: {message}")

    async def receive_message(self):
        number = random.randint(0, 2)
        await asyncio.sleep(0.1)
        if number == 0:
            return {"command": "set_camera_iso", "value": 23}
        elif number == 1:
            return {"command": "set_camera_iso", "value": 120}
        else:
            return {"command": "ping", "value": None}
