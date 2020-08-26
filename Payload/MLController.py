import os
from Payload.exceptions import MLControllerException


class MLController:
    def __init__(self, model_dir: str = "./Payload/models"):
        self.__active_models = {}
        self.__inactive_models = {}
        self.__model_dir = model_dir
        self.__model_import_path = ".".join(model_dir.split("/")[1:])
        for path in os.listdir(self.__model_dir):
            if path[0:2] != "__":
                name = path[0:-3]
                module = __import__(f"{self.__model_import_path}.{name}", fromlist=[name])
                my_class = getattr(module, name)
                self.__inactive_models[name] = my_class()

    async def start_model(self, name: str) -> bool or MLControllerException:
        if name in self.__inactive_models:
            self.__inactive_models[name].start()
            return True
        elif name in self.__active_models:
            return MLControllerException("Model already active")
        else:
            return MLControllerException("Invalid model name")

    async def stop_model(self, name: str) -> bool or MLControllerException:
        if name in self.__inactive_models:
            self.__active_models[name].stop()
            return True
        elif name in self.__inactive_models:
            return MLControllerException("Model not active")
        else:
            return MLControllerException("Invalid model name")

    async def register_model(self, name: str) -> bool or MLControllerException:
        if not os.path.exists(f"{self.__model_dir}/{name}.py"):
            return MLControllerException("Model file not found")
        module = __import__(f"{self.__model_import_path}.{name}", fromlist=[name])
        my_class = getattr(module, name)
        self.__inactive_models[name] = my_class()
        return True
