import asyncio
from utils import get_redis_client, config, run, validate_json
import json
import base64
import numpy as np


async def main():
    sub = await get_redis_client()
    pub = await get_redis_client()
    pattern, = await sub.subscribe(config["CHANNELS"]["CAM-RES"])  # read all channels prefixed with `SOME_`

    while await pattern.wait_message():
        data = await pattern.get()
        validate_json(json.loads(data))
        message = json.loads(data.decode())
        img = base64.b64decode(message["data"].encode())
        img = np.frombuffer(img, dtype=np.float64)

        # run model inference here
        print(img.tolist()[0:30])

        #change out message once inference is implemented
        await pub.publish(config["CHANNELS"]["FC-OUT"], data)
        await asyncio.sleep(1)


if __name__ == "__main__":
    run(main)