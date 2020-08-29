import asyncio
import json
from utils import get_redis_client, validate_json, config, run

TEST = config["TESTING"].getboolean("TEST")
device = None

if not TEST:
    import serial
    device = serial.Serial("/dev/serial0", 9600)


async def main():
    sub = await get_redis_client()
    pattern, = await sub.subscribe(config["CHANNELS"]["FC-OUT"])
    loop = asyncio.get_event_loop()
    while await pattern.wait_message():
        data = await pattern.get()
        validate_json(json.loads(data))
        message = data + "\n".encode()
        if TEST:
            print(f"{message[0:10]}...")
        else:
            await loop.run_in_executor(None, device.write, message)


if __name__ == "__main__":
    run(main)
