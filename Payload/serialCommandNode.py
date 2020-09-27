import asyncio
import json
from utils import get_redis_client, config, run


async def main():
    sub = await get_redis_client()
    pub = await get_redis_client()
    (pattern,) = await sub.subscribe(
        config["CHANNELS"]["FC-IN"]
    )  # read all channels prefixed with `SOME_`

    while await pattern.wait_message():
        data = await pattern.get()
        message = json.loads(data)
        if message["command"] == config["COMMANDS"]["TAKE-IMG"]:
            print(f"Got valid message {message}")
            await pub.publish(config["CHANNELS"]["CAM-COM"], data)
        else:
            print(f"Unknown serial command {message}")


if __name__ == "__main__":
    run(main)