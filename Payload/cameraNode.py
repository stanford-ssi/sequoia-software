import asyncio
import base64
import json
import os
import secrets
from datetime import datetime
from random import randint

import numpy as np
from skimage import color, io
from skimage.transform import resize

import utils

logger = utils.get_sequoia_logger()

TEST = utils.config["TESTING"].getboolean("TEST")
CAMERA = None

if not TEST:
    import picamera

    CAMERA = picamera.PiCamera()
    CAMERA.resolution = utils.config["CAMERA"].gettuple("RESOLUTION")


async def main():
    sub = await utils.get_redis_client()
    pub = await utils.get_redis_client()

    if not os.path.exists("./images"):
        os.mkdir("./images")

    (pattern,) = await sub.subscribe(utils.config["CHANNELS"]["CAM-COM"])

    output_buffer = np.empty(
        (
            utils.config["CAMERA"].gettuple("RESOLUTION")[1],
            utils.config["CAMERA"].gettuple("RESOLUTION")[0],
            3,
        ),
        dtype=np.float64,
    )
    loop = asyncio.get_running_loop()
    while await pattern.wait_message():
        data = await pattern.get()
        message = json.loads(data)
        if message["command"] == utils.config["COMMANDS"]["TAKE-IMG"]:
            logger.info("Taking IMG")
            if TEST:
                if randint(0, 1):
                    output_buffer = io.imread("Earth_1.png")
                else:
                    output_buffer = io.imread("Earth_2.png")
            else:
                await loop.run_in_executor(None, CAMERA.capture, output_buffer, "rgb")
            image_resized = resize(output_buffer, (300, 300, 4), anti_aliasing=True)
            io.imsave(
                f"./images/{datetime.utcnow().strftime('%Y-%m-%d %H-%M-%S')}--{secrets.token_urlsafe(10)}.png",
                image_resized,
            )
            logger.info(f"Cropped to {image_resized.shape}")
            message["data"] = base64.b64encode(image_resized).decode()
            await pub.publish_json(utils.config["CHANNELS"]["CAM-RES"], message)
        else:
            logger.warning(f"Unknown camera command {message}")


if __name__ == "__main__":
    utils.run(main)
