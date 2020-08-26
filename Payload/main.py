import asyncio
from actions import command_handler
#from dummyCamera import DummyCamera
from radio import Radio
from RaspiCam import RaspiCam
from FcBus import FcBUS

camera = RaspiCam()
radio = Radio()
fc_bus = FcBUS()

command_handler.camera = camera
command_handler.radio = radio
command_handler.fc_bus = fc_bus


async def flight_controller_communication_loop():
    while True:
        new_message = await fc_bus.receive_message()
        if new_message:
            print(new_message)
        else:
            print(f"No message received.\n")
        await fc_bus.send_message({"type": "message", "value": "Hello!"})
        await asyncio.sleep(1)


async def main():
    for i in range(0, 15):
        await command_handler.handle({"command": "print_image_data"})
        await asyncio.sleep(1)
    return


async def image_demo():
    while True:
        new_message = await fc_bus.receive_message()
        if new_message:
            print(await command_handler.handle(new_message))
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(image_demo())
