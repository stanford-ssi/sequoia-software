import json
from utils import validate_json, get_redis_client, config, run
import asyncio

TEST = config["TESTING"].getboolean("TEST")
device = None

if not TEST:
    import serial
    device = serial.Serial("/dev/serial0", 9600)


async def main():
    pub = await get_redis_client()
    loop = asyncio.get_event_loop()
    while True:
        if TEST:
            await asyncio.sleep(5)
            data = config["TEST-MSG"]["IMG-TEST"]
        else:
            data = await loop.run_in_executor(None, device.read_until)
        msg = json.loads(data)
        if validate_json(msg):
            await pub.publish(config["CHANNELS"]["FC-IN"], data)
        else:
            print(f"Invalid serial in {msg}")

if __name__ == "__main__":
    run(main)