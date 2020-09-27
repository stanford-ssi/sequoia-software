import asyncio
import json

import utils

TEST = utils.config["TESTING"].getboolean("TEST")
device = None

if not TEST:
    import serial

    device = serial.Serial("/dev/serial0", 9600)


async def main():
    sub = await utils.get_redis_client()
    (pattern,) = await sub.subscribe(utils.config["CHANNELS"]["FC-OUT"])
    loop = asyncio.get_event_loop()
    while await pattern.wait_message():
        data = await pattern.get()
        utils.validate_json(json.loads(data))
        message = data + "\n".encode()
        if TEST:
            print(f"{message[0:10]}...")
        else:
            await loop.run_in_executor(None, device.write, message)


if __name__ == "__main__":
    utils.run(main)
