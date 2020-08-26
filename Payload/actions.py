from commandHandler import CommandHandler

command_handler = CommandHandler()


@command_handler.register_command
async def set_camera_iso(handler: CommandHandler, command: dict) -> bool:
    handler.camera.iso = command["value"]
    return True


@command_handler.register_command
async def ping(handler: CommandHandler, *args) -> bool:
    await handler.radio.send_message({"payload": "I'm still alive!"})
    return True


@command_handler.register_command
async def print_image_date(handler: CommandHandler, *args) -> bool:
    output = await handler.radio.take_image()
    print(output[0:10])
    return True


@command_handler.register_command
async def take_image(handler: CommandHandler, *args) -> bool:
    img = await handler.camera.take_image()
    response = {
        "code": 200,
        "img_shape": str(img.shape)
    }
    return await handler.fc_bus.send_message(response)
