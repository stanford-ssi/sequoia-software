import asyncio
from utils import get_redis_client, config, run, validate_json
import json
import base64
import numpy as np

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

app = App("imageProcessor", {})

@app.subscribe(config["CHANNELS"]["CAM-RES"], message_schema)
async def receive_message(msg, redis, cache):
    img = base64.b64decode(msg["data"].encode())
    img = np.frombuffer(img, dtype=np.float64)

    # run model inference here
    print(img.tolist()[0:30])

    # change out message once inference is implemented
    return config["CHANNELS"]["FC-OUT"], msg


if __name__ == "__main__":
    app.run({})