import json
from datetime import datetime


class Message():
    def __init__(self, time=None, origin=None, data=None):
        self.time = time
        if self.time is None:
            self.time = datetime.utcnow()
        self.data = data
        self._origin = None
        self.origin = origin

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, new_val):
        if isinstance(new_val, str) or new_val == None:
            self._origin = new_val
        else:
            raise ValueError("Invalid datatype for attribute 'origin'")

    def toBytes(self):
        return self.encode().encode()

    def encode(self):
        message = {}
        message["time"] = self.time.isoformat()
        message["data"] = self.data
        message["origin"] = self.origin
        return json.dumps(message)

    def decode(self, message):
        new_values = json.loads(message)
        self.time = datetime.fromisoformat(new_values["time"])
        self.origin = new_values["origin"]
        self.data = new_values["data"]
