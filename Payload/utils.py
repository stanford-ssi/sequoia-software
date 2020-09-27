import asyncio
import configparser
import logging
import signal

import aioredis


def parse_int_tuple(input):
    return tuple(int(k.strip()) for k in input[1:-1].split(","))


config = configparser.ConfigParser(converters={"tuple": parse_int_tuple})
config.read("config.ini")


def get_sequoia_logger() -> logging.Logger:
    """Get a logging object with Sequoia-specific settings."""
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s %(module)s.%(funcName)s.%(lineno)d %(message)s"
    )
    return logging.getLogger()


def validate_json(data: dict) -> bool:
    """Helper function to validate json messages that come into
    the satellite or will be sent out of the satellite"""
    try:
        assert "data" in data.keys()
        assert isinstance(data["data"], str)
        assert "command" in data.keys()
        assert isinstance(data["command"], str)
        assert "time" in data.keys()
        assert isinstance(data["time"], str)
        assert "origin" in data.keys()
        assert isinstance(data["origin"], str)
        return True
    except AssertionError:
        return False


async def get_redis_client() -> aioredis.Redis:
    return await aioredis.create_redis(config["REDIS"]["ADDRESS"])


async def shutdown(signal, loop):
    """Cleanup tasks tied to the service's shutdown."""
    print(f"Received exit signal {signal.name}...")
    print("Closing redis connections")
    print("Nacking outstanding messages")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    [task.cancel() for task in tasks]

    print(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    print(f"Flushing metrics")
    loop.stop()


def run(func):
    loop = asyncio.get_event_loop()
    # May want to catch other signals too
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(s, loop)))

    try:
        loop.create_task(func())
        loop.run_forever()
    finally:
        loop.close()
        print(f"Successfully shutdown")
