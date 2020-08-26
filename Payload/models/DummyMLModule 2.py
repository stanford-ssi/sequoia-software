import keras
from Payload.MLModuleABC import MLModule
from Payload.exceptions import ModelNotFound


class DummyMLModule(MLModule):
    def __init__(self):
        self.model = None

    async def process(self, data: dict) -> dict:
        if self.model is None:
            raise ModelNotFound
        return self.model.predict(data["data"])

    async def start(self, model):
        self.model = keras.models.load_model(model)
        return True

    async def stop(self) -> bool:
        self.model = None
        return True