import board
import busio
import time
import digitalio
import json

uart = busio.UART(board.PB16, board.PB17, baudrate=9600, receiver_buffer_size=256)

testdata = {"hello": "Moritz", "How": "AreYouDoing"}


def send_message(raw):
    payload = json.dumps(raw) + "\n"
    b = bytearray()
    b.extend(payload)
    numBytes = uart.write(b)
    return numBytes
    # print("Wrote message to Pi (" + str(numBytes) + "): " + payload)


def listen():
    # waits until response
    while True:
        if uart.in_waiting:
            data = uart.readline()
            return data


def handle_message(msg):
    result = msg.decode('utf-8')
    print(result)


def take_image():
    data = {"command": "take_image"}
    send_message(data)
    return listen()
    # checks if bytes in UART buffer
    # Reads line of data as bytes
    # count += 1
    # if count % 10 == 0:
    #    sendMessage(testdata)
