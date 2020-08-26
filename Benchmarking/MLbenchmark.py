import keras
from keras.applications.resnet50 import ResNet50
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
import os
import time

#model = ResNet50(weights='imagenet')
#model = keras.applications.resnet.ResNet101(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=1000)
#output_file = "resnet50_time.txt"

def runTest(model, of, size):
    rootdir = "/home/pi/Documents/images"
    output_file = "out/" + of
    print("STARTING TEST FOR -- " + of.upper().replace(".TXT", ""))
    start = time.time()
    count = 0

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            img_path = os.path.join(subdir, file)
            #img_path = 'images/ant/image_0001.jpg'
            img = image.load_img(img_path, target_size=(size, size))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)

            preds = model.predict(x)
            
            count+=1
            print(count)
            if (count % 10 == 0):
                #print(time.time()-start)
                with open(output_file, 'a') as f:
                    f.write(str(time.time()-start) + "\n")
                    
                start = time.time()
            if (count == 1000):
                return
            # decode the results into a list of tuples (class, description, probability)
            # (one such list for each sample in the batch)
            #print('Predicted:', decode_predictions(preds, top=3)[0])

# poor programming practice but min memory usage
#model = keras.applications.resnet.ResNet50(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=1000)
#outFile = "resnet50.txt"
#runTest(model, outFile, 224)

#model = keras.applications.resnet.ResNet101(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=1000)
#outFile = "resnet101.txt"
#runTest(model, outFile, 224)

#model = keras.applications.resnet.ResNet152(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=1000)
#outFile = "resnet152.txt"
#runTest(model, outFile, 224)

#model = keras.applications.inception_v3.InceptionV3(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=1000)
#outFile = "inceptionv3.txt"
#runTest(model, outFile, 299)

#model = keras.applications.inception_resnet_v2.InceptionResNetV2(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=1000)
#outFile = "inceptionresnetv2.txt"
#runTest(model, outFile, 299)

model = keras.applications.mobilenet.MobileNet(input_shape=None, alpha=1.0, depth_multiplier=1, dropout=1e-3, include_top=True, weights='imagenet', input_tensor=None, pooling=None, classes=1000)
outFile = "mobilenet.txt"
runTest(model, outFile, 224)

model = keras.applications.densenet.DenseNet121(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=1000)
outFile = "densenet121.txt"
runTest(model, outFile, 224)

model = keras.applications.nasnet.NASNetMobile(input_shape=None, include_top=True, weights='imagenet', input_tensor=None, pooling=None, classes=1000)
outFile = "nasnetmobile.txt"
runTest(model, outFile, 224)

model = keras.applications.nasnet.NASNetLarge(input_shape=None, include_top=True, weights='imagenet', input_tensor=None, pooling=None, classes=1000)
outFile = "nasnetlarge.txt"
runTest(model, outFile, 331)
