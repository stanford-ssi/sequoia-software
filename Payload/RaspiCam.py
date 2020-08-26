import picamera
import numpy as np


class RaspiCam:
    def __init__(self):
        self._camera = picamera.PiCamera()

    async def take_image(self):
        output = np.empty((self._camera.resolution[1], self._camera.resolution[0], 3))
        self._camera.capture(output, "rgb")
        return output
