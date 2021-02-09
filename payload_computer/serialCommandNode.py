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

app = App("serialCommand", {})

@app.subscribe(config["CHANNELS"]["FC-IN"], message_schema)
async def receive_message(msg, redis, cache):
    if msg["command"] == config["COMMANDS"]["TAKE-IMG"]:
        logger.info(f"Got valid message {msg}")
        return config["CHANNELS"]["CAM-COM"], msg
    else:
        logger.warning(f"Unknown serial command {msg}")

if __name__ == "__main__":
    app.run({})
