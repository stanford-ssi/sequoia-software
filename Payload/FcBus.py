import serial
import json
import asyncio


class FcBUS:
    def __init__(self, path="/dev/serial0", baud=9600):
        self._serial = serial.Serial(path, baud)
        self._path = path
        self._baud = baud

    async def receive_message(self) -> dict or False:
        if self._serial.in_waiting > 0:
            msg = self._serial.read_until()
            #print(1)
            #print(msg)
            #print(type(msg))
            msg = msg.decode()
            #print(2)
            #print(msg)
            #print(type(msg))
            msg = json.loads(msg)
            #print(3)
            #print(msg)
            #print(type(msg))
            return msg

    async def send_message(self, message: dict) -> bool:
        encoded_message = json.dumps(message).encode() + "\n".encode()
        self._serial.write(encoded_message)
        return True
