import random
from typing import List


class ObjectCreator(object):

    def __init__(self, name: str):
        self.name = name
        self.curVal = None

    def set_value(self, new_val: str) -> bool:
        self.curVal = new_val
        return True

    def get_value(self) -> str:
        return self.curVal

    @staticmethod
    def get_random_numbers(min: int, max: int, len: int) -> List[int]:
        return [random.randint(min, max) for i in range(len)]

