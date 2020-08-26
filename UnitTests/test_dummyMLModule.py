import numpy as np
from Payload.models.DummyMLModule import DummyMLModule
import keras
from keras import layers
import asyncio
import unittest


class TestDummyMLModule(unittest.TestCase):

    async def _test_load_model(self):
        data = np.random.random((1000, 32))
        labels = np.random.random((1000, 10))

        model = keras.Sequential([
            layers.Dense(10, activation='softmax', input_shape=(32,)),
            layers.Dense(10, activation='softmax')
        ])
        model.compile(optimizer='rmsprop',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        model.fit(data, labels, batch_size=32, epochs=5)

        # Save entire model to a HDF5 file
        model.save('my_model.h5')

        # Recreate the exact same model, including weights and optimizer.
        dummyMod = DummyMLModule()
        await dummyMod.start('my_model.h5')
        testData = {"data": np.random.randint(0, 10, (1,32))}
        print(await dummyMod.process(testData))
        await dummyMod.stop()

    def test_load_model(self):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self._test_load_model())
        loop.close()
