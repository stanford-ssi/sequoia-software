import json
import asyncio
from redis_wrapper.app import App
from utils import validate_json, config

TEST = config["TESTING"].getboolean("TEST")
device = None

if not TEST:
    import serial

    device = serial.Serial("/dev/serial0", 9600)

app = App("serialIn", {})

@app.interval(0)
async def send_new_value(_, redis, cache):
    if TEST:
        await asyncio.sleep(5)
        data = config["TEST-MSG"]["IMG-TEST"]
    else:
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, device.read_until)

    msg = json.loads(data)
    if validate_json(msg):
        print(f"Sending to channel {config['CHANNELS']['FC-IN']}: {json.dumps(data, indent=4)}")
        return config["CHANNELS"]["FC-IN"], data
    return None, None


if __name__ == "__main__":
    app.run({})