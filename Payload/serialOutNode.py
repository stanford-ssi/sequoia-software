import json
import asyncio

from redis_wrapper.app import App
from utils import validate_json, config, get_sequoia_logger

message_schema = {
        "type": "object",
        "properties": {
            "data": {
                "type": "string"
            },
            "time": {
                "type": "string"
            }, 
            "origin": {
                "type": "string"
            }, 
            "command": {
                "type": "string"
            }
        },
        "required": ["data", "time", "origin", "command"]
    }

logger = get_sequoia_logger()

TEST = config["TESTING"].getboolean("TEST")
device = None

if not TEST:
    import serial

    device = serial.Serial("/dev/serial0", 9600)

app = App("serialOut", {})

@app.subscribe(config["CHANNELS"]["FC-OUT"], message_schema)
async def receive_message(msg, redis, cache):
    if TEST:
        logger.info(f"{msg['data'][0:10]}...")
    else:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, device.write, json.dumps(msg))

if __name__ == "__main__":
    app.run({})
