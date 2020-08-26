import keras
from MLbenchmark import runMLTest
from PIL import Image
import numpy as np
import requests
from time import sleep, time
from multiprocessing import Process
import argparse
from picamera import PiCamera
import random
from uuid import uuid4

def run_test(name, file, cam, test, enable_output):
    print("############################################")
    print(f"Running test {name}\n")
    t1 = time()
    file.write(f"{name}\n")
    file.write(f"start time: {t1}\n")
    start_img_name = f"{name}:start:{str(uuid4)}.jpg"
    end_img_name = f"{name}:end:{str(uuid4)}.jpg"
    cam.capture(start_img_name)
    file.write(f"start img: {start_img_name}\n")
    test(enable_output)
    t2 = time()
    file.write(f"end time: {t2}\n")
    file.write(f"duration: {t2-t1}\n")
    cam.capture(end_img_name)
    file.write(f"end img: {end_img_name}\n\n")
    print(f"Done with test {name}")
    print("############################################\n\n")


def test_idle(enable_output):
    for i in range(200):
        res = requests.get("https://www.google.at/")
        if enable_output and (i % 25 == 0):
            print(i)
        sleep(0.01)


def test_processes(enable_output):
    procs = []
    for i in range(50):
        procs.append(Process(target=test_idle, args=[enable_output,]))
    for p in procs:
        p.start()
    for p in procs:
        p.join()


def test_full(enable_output):
    for i in range(1000):
        im = np.array(Image.open('/home/pi/test.jpg'))
        mat1 = np.random.rand(900, 1440, 3)
        mat2 = np.random.rand(1, 900, 1440)
        im = im * mat1
        im = np.matmul(mat2, im)
        if enable_output and (i % 100 == 0):
            print(i)


def test_ml(enable_output):
    rootdir = "/home/pi/Documents/images"
    model = keras.applications.mobilenet.MobileNet(input_shape=None, alpha=1.0, depth_multiplier=1, dropout=1e-3,
     include_top=True, weights='imagenet', input_tensor=None, pooling=None, classes=1000)
    count = 0
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            img_path = os.path.join(subdir, file)
            img = image.load_img(img_path, target_size=(224, 224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)

            preds = model.predict(x)

            count+=1
            if enable_output and (count % 50 == 0):
                print(count)
            if (count == 1000):
                return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("test_type")
    parser.add_argument("outputfile")
    args = parser.parse_args()
    cam = PiCamera()
    with open(args.outputfile, "w+") as f:
        if "i" in args.test_type:
            run_test("idle-test", f, cam, test_idle, true)
        if "p" in args.test_type:
            run_test("multi-process-test", f, cam, test_processes, true)
        if "f" in args.test_type:
            run_test("full-matrix-ops-test", f, cam, test_full, true)
        if "m" in args.test_type:
            run_test("ML-image-proc-test", f, cam, test_ml, true)
        print("\nDone\n")