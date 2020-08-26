from exceptions import HandlerException
import asyncio


class CommandHandler:
    def __init__(self):
        self.__camera = None
        self.__radio = None
        self.__fc_bus = None
        self.__ml_module = None
        self.__commands = {}

    async def handle(self, command: dict) -> object:
        if command["command"] in self.__commands:
            try:
                return await self.__commands[command["command"]](self, command)
            except Exception as e:
                return HandlerException(e)
        else:
            return HandlerException("Invalid command")

    def register_command(self, func):
        self.__commands[func.__name__] = func
        return True

    @property
    def camera(self):
        return self.__camera

    @camera.setter
    def camera(self, cam):
        self.__camera = cam

    @property
    def radio(self):
        return self.__radio

    @radio.setter
    def radio(self, radio):
        self.__radio = radio

    @property
    def fc_bus(self):
        return self.__fc_bus

    @fc_bus.setter
    def fc_bus(self, bus):
        self.__fc_bus = bus

    @property
    def ml_module(self):
        return self.__ml_module

    @ml_module.setter
    def ml_module(self, module):
        self.__ml_module = module
