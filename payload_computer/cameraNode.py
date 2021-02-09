import asyncio
import base64
import json
import os
import secrets
from datetime import datetime
from random import randint

import numpy as np
from skimage import io
from skimage.transform import resize

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

app = App("camera", {})

TEST = config["TESTING"].getboolean("TEST")
CAMERA = None

if not TEST:
    import picamera

    CAMERA = picamera.PiCamera()
    CAMERA.resolution = config["CAMERA"].gettuple("RESOLUTION")

@app.subscribe(config["CHANNELS"]["CAM-COM"], message_schema)
async def receive_message(msg, redis, cache):
    print("Got camera command")
    output_buffer = np.empty(
        (
            config["CAMERA"].gettuple("RESOLUTION")[1],
            config["CAMERA"].gettuple("RESOLUTION")[0],
            3,
        ),
        dtype=np.float64,
    )
    if msg["command"] == config["COMMANDS"]["TAKE-IMG"]:
        logger.info("Taking IMG")
        if TEST:
            if randint(0, 1):
                output_buffer = io.imread("Earth_1.png")
            else:
                output_buffer = io.imread("Earth_2.png")
        else:
            CAMERA.capture(output_buffer, "rgb")
        image_resized = resize(
            output_buffer, (300, 300, 4), anti_aliasing=True)
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H-%M-%S')
        io.imsave(
            f"./images/{timestamp}--{secrets.token_urlsafe(10)}.png",
            image_resized,
        )
        logger.info(f"Cropped to {image_resized.shape}")
        msg["data"] = base64.b64encode(image_resized).decode()
        return config["CHANNELS"]["CAM-RES"], msg
    else:
        logger.warning(f"Unknown camera command {msg}")


if __name__ == "__main__":
    if not os.path.exists("./images"):
        os.mkdir("./images")
    app.run({})
