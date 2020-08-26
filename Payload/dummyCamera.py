import cv2
import random


class DummyCamera:
    def __init__(self, image_paths=["/Users/moritzstephan/Downloads/Meme.jpg"]):
        self.__iso = None
        self.__images = [cv2.imread(path) for path in image_paths]

    @property
    def iso(self):
        return self.__iso

    @iso.setter
    def iso(self, value):
        if not -15 <= value <= 30:
            raise ValueError("Invalid Radio ISO")
        self.__iso = value

    async def take_image(self):
        return random.choice(self.__images)
