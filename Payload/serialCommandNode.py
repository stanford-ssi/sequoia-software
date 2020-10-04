import json

import utils


logger = utils.get_sequoia_logger()


async def main():
    sub = await utils.get_redis_client()
    pub = await utils.get_redis_client()
    (pattern,) = await sub.subscribe(
        utils.config["CHANNELS"]["FC-IN"]
    )  # read all channels prefixed with `SOME_`

    while await pattern.wait_message():
        data = await pattern.get()
        message = json.loads(data)
        if message["command"] == utils.config["COMMANDS"]["TAKE-IMG"]:
            logger.info(f"Got valid message {message}")
            await pub.publish(utils.config["CHANNELS"]["CAM-COM"], data)
        else:
            logger.warning(f"Unknown serial command {message}")


if __name__ == "__main__":
    utils.run(main)
