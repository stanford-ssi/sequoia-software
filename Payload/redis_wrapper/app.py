import json
import signal
import asyncio
import aioredis
import traceback
from logging import Logger
from jsonschema import validate
from typing import Callable, List, Tuple, Any, Dict

class App:
    def __init__(self, name: str, storage_schema: Dict[str, Any]):
        self._name: str = name
        self._storage_schema: Dict[str, Any] = storage_schema
        self._channels: List[Tuple[str, Callable]] = []
        self._startup: Callable = None
        self._intervals: List[Tuple[float, Callable]] = []
        self._storage: Dict[str, Any] = {}
        self._redis_subscriber: aioredis.Redis = None
        self._redis_publisher: aioredis.Redis = None
        self._logger: Logger = None

    def subscribe(self, channel: str, schema: Dict[str, Any]) -> Callable:
        def decorator(fn: Callable) -> Callable:
            async def callback_wrapper(channel: aioredis.Channel):
                async for message in channel.iter():
                    try:
                        self._logger.debug(f"Got {message} of type {type(message)} on {channel.name.decode()} at {self._name}")
                        msg = json.loads(message)
                        validate(instance=msg, schema=schema)
                        tmp = self._storage.copy()
                        ret_val = await fn(msg, self._redis_publisher, tmp)
                        validate(instance=tmp, schema=self._storage_schema)
                        self._storage = tmp
                        if ret_val != None and not isinstance(ret_val, tuple) and len(ret_val) != 2 and not isinstance(ret_val[0], string) and not isinstance(ret_val[1], dict):
                            raise ValueError("Callback needs to return either None our channel name <string>, message <dict> tuple")
                        elif ret_val != None:
                            self._logger.debug(f"Sending {json.dumps(ret_val[1])} of type {type(json.dumps(ret_val[1]))} on {channel.name.decode()} at {self._name}")
                            self._redis_publisher.publish(ret_val[0], json.dumps(ret_val[1]))
                    except Exception as e:
                        self._logger.error(f"Exception occured in callback {channel.name.decode()} of {self._name}: {traceback.format_exc()}")
            self._channels.append((channel, callback_wrapper))
            return fn
        return decorator


    def startup(self, fn: Callable) -> Callable:
        async def startup_wrapper():
            try:
                tmp = self._storage.copy()
                return_channel, return_message = await fn({}, self._redis_publisher, tmp)
                validate(instance=tmp, schema=self._storage_schema)
                self._storage = tmp
                if return_channel and return_message:
                    self._redis_publisher.publish(return_channel, json.dumps(return_message))
            except Exception as e:
                self._logger.error(f"Exception occured in callback startup callback of {self._name}: {traceback.format_exc()}")
        self._startup = startup_wrapper
        return fn

    def interval(self, timeout: float):
        def decorator(fn: Callable) -> Callable:
            async def callback_wrapper(timeout: float):
                while True:
                    try:
                        tmp = self._storage.copy()
                        return_channel, return_message = await fn({}, self._redis_publisher, tmp)
                        validate(instance=tmp, schema=self._storage_schema)
                        self._storage = tmp
                        if return_channel and return_message:
                            self._redis_publisher.publish(return_channel, json.dumps(return_message))
                        await asyncio.sleep(timeout)
                    except Exception as e:
                        self._logger.error(f"Exception occured in callback interval of {self._name}: {traceback.format_exc()}")
            self._intervals.append((timeout, callback_wrapper))
            return fn
        return decorator

    async def _activate_subscriptions(self):
        for name, callback in self._channels:
            channel = await self._redis_subscriber.subscribe(name)
            asyncio.get_running_loop().create_task(callback(channel[0]))

    async def _activate_intervals(self):
        for interval, callback in  self._intervals:
            asyncio.get_running_loop().create_task(callback(interval))

    async def _shutdown(self, signal, loop):
        """Cleanup tasks tied to the service's shutdown."""
        print(f"Received exit signal {signal.name}...")
        print("Closing redis connections")
        self._redis_subscriber.close()
        self._redis_publisher.close()
        await self._redis_subscriber.wait_closed()
        await self._redis_publisher.wait_closed()
        print("Nacking outstanding messages")
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

        [task.cancel() for task in tasks]

        print(f"Cancelling {len(tasks)} outstanding tasks")
        await asyncio.gather(*tasks, return_exceptions=True)
        print(f"Flushing metrics")
        loop.stop()

    def run(self, storage: Dict[str, Any], redis_host: str = "localhost", \
            redis_port: str = "6379", redis_password: str = None, logger: Logger = None):

        self._storage = storage

        if logger is None:
            self._logger = Logger(self._name)
        else:
            self._logger = logger

        async def _run():
            try:
                self._redis_subscriber = await aioredis.create_redis(f"redis://{redis_host}:{redis_port}", password=redis_password)
                self._redis_publisher = await aioredis.create_redis(f"redis://{redis_host}:{redis_port}", password=redis_password)
            except Exception as e:
                logger.error(f"Failed to initialize redis: {e}")
                raise e
            if self._startup:
                await self._startup()
            await self._activate_subscriptions()
            await self._activate_intervals()

        loop = asyncio.get_event_loop()
        # May want to catch other signals too
        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for s in signals:
            loop.add_signal_handler(s, lambda s=s: asyncio.create_task(self._shutdown(s, loop)))

        try:
            loop.create_task(_run())
            loop.run_forever()
        finally:
            loop.close()
            print(f"Successfully shutdown")