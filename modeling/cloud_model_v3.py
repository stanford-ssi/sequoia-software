# scrape the USGS website
# and deal with file directories
from bs4 import BeautifulSoup
from pathlib import Path
import requests

# extraction and download parallel processing
import multiprocessing as mp
import subprocess
import functools
import glob
import os 

# for converting .img files to .TIF
# because the USGS stores things weirdly
from osgeo import gdal

# machine learning
import tensorflow as tf
import tensorflow_io as tfio
from tf.keras import layers


def get_asset_links(url='https://landsat.usgs.gov/landsat-8-cloud-cover-assessment-validation-data'):
    # landsat 8 data, should be 96 folders of the following form:
    # 'https://landsat.usgs.gov/cloud-validation/cca_l8/LC80420082013220LGN00.tar.gz'
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    # web scrape usgs website for the links to each of the 96 cloud cover images
    links = []
    for link in soup.find_all('a'):
        link = link.get('href')
        criterion1 = 'https://landsat.usgs.gov/cloud-validation/cca_l8/'
        criterion2 = 'tar.gz'
        if link is not None and criterion1 in link and criterion2 in link:
          links.append(link)
    return links


def write_links_to_file(links, fname='links.txt'):
    with open(fname, 'w') as f:
        for item in links:
            f.write("%s\n" % item)
    return fname


def download_assets(fname, directory):
    os.system(f"mkdir {directory}")
    os.system(f"aria2c -s16 -x16 -d {directory} -i {fname}")
    return directory


def untar_and_delete(file, out_dir):
    subprocess.call(['tar', '-xvf', file, '--directory', out_dir])
    subprocess.call(['rm', file])
    file = out_dir + '/BC/' + file.replace('.tar.gz', '')
    return file


def extract(in_dir, out_dir):
    files = glob.glob(f"{in_dir}/*.tar.gz")
    untarrer = functools.partial(untar_and_delete, out_dir=out_dir)
    
    with mp.Pool(mp.cpu_count()) as p:
        extracted_files = p.map(untarrer, files)
    return extracted_files


def make_ds_from_assets(assets):
    # bands 2,3,4 are BGR (in that order), according to:
    # https://www.usgs.gov/faqs/what-are-band-designations-landsat-satellites?
    # qt-news_science_products=0#qt-news_science_products
    ds = []
    for asset in assets:
      blue, green, red, mask = None, None, None, None
      paths = [str(path) for path in Path(asset).rglob('*_*')]
      for path in paths:
        if 'B2' in path: blue = path
        elif 'B3' in path: green = path
        elif 'B4' in path: red = path
        elif 'fixedmask.img' in path: 
         mask = path.replace('.img', '.TIF')
         input = gdal.Translate(mask, gdal.Open(path), format="GTiff")
         input = None 

      images = (red, green, blue, mask)
      # some times download gets corrupted, if so, throw that row away
      if None in images: pass
      else: ds.append(images)

    # dataset where each row is a tuple of paths for red, green, blue, and mask
    # where each path points to a .TIF file
    ds = tf.data.Dataset.from_tensor_slices(ds)
    return ds


@tf.function
def read_img_and_mask(files):
    # read img at specified path
    r, g, b, mask = files[0], files[1], files[2], files[3]

    # read in each band and the mask as tiff files. 
    # tf reads this as RGBE, but, each is essentially single band
    # (including the mask), not the 4 bands tf expects
    # so strip out 'R', because 'R' 'G' 'B' bands are all (verifiably) equal. 
    # E is meaningless (all 255), so we dont use it
    r, g, b, mask = map(
        lambda x: tfio.experimental.image.decode_tiff(tf.io.read_file(x))[:, :, 0], 
        [r, g, b, mask])
    img = tf.experimental.numpy.dstack((r, g, b))

    # 'https://landsat.usgs.gov/cloud-validation/cca_l8/LC80420082013220LGN00.tar.gz'
    # the mask values correspond to the following classes:
    # Fill 0, Cloud Shadow 64, Clear 128, Thin Cloud 192, Cloud 255
    thin_cloud = tf.where(mask == 192, True, False)
    cloud = tf.where(mask == 255, True, False)
    mask = tf.math.logical_or(thin_cloud, cloud)

    return img, mask


@tf.function
def sample_crop(img, mask, h, w, n):
  # take n random crops of size h, w from an image and its mask 
  # stack mask and image s.t. we crop both at the same time
  img_and_mask = tf.experimental.numpy.dstack((img, mask))
  crops = [tf.image.random_crop(img_and_mask, (h, w, 4)) for i in range(n)]
  # convert the n stacked, cropped images into a dataset
  crops = tf.stack(crops)
  crops = tf.data.Dataset.from_tensor_slices(crops)
  return crops



def build_unet_segmentation_model(h, w, c):
    # UNet Semantic Segmentation Architecture

    # Build the model
    inputs = layers.Input((h, w, c))
    s = layers.experimental.preprocessing.Rescaling(1.0 / 255)(inputs)

    # Contraction path
    c1 = layers.Conv2D(16, (3, 3), activation='relu', padding='same')(s)
    c1 = layers.Dropout(0.1)(c1)
    c1 = layers.Conv2D(16, (3, 3), activation='relu', padding='same')(c1)
    p1 = layers.MaxPooling2D((2, 2))(c1)

    c2 = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(p1)
    c2 = layers.Dropout(0.1)(c2)
    c2 = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(c2)
    p2 = layers.MaxPooling2D((2, 2))(c2)

    c3 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(p2)
    c3 = layers.Dropout(0.2)(c3)
    c3 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(c3)
    p3 = layers.MaxPooling2D((2, 2))(c3)

    c4 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(p3)
    c4 = layers.Dropout(0.2)(c4)
    c4 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(c4)
    p4 = layers.MaxPooling2D(pool_size=(2, 2))(c4)

    c5 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(p4)
    c5 = layers.Dropout(0.3)(c5)
    c5 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(c5)

    #Expansive path 
    u6 = layers.Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(c5)
    u6 = layers.concatenate([u6, c4])
    c6 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(u6)
    c6 = layers.Dropout(0.2)(c6)
    c6 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(c6)

    u7 = layers.Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(c6)
    u7 = layers.concatenate([u7, c3])
    c7 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(u7)
    c7 = layers.Dropout(0.2)(c7)
    c7 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(c7)

    u8 = layers.Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same')(c7)
    u8 = layers.concatenate([u8, c2])
    c8 = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(u8)
    c8 = layers.Dropout(0.1)(c8)
    c8 = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(c8)

    u9 = layers.Conv2DTranspose(16, (2, 2), strides=(2, 2), padding='same')(c8)
    u9 = layers.concatenate([u9, c1], axis=3)
    c9 = layers.Conv2D(16, (3, 3), activation='relu', padding='same')(u9)
    c9 = layers.Dropout(0.1)(c9)
    c9 = layers.Conv2D(16, (3, 3), activation='relu', padding='same')(c9)

    outputs = layers.Conv2D(1, (1, 1), activation='sigmoid')(c9)

    model = tf.keras.Model(inputs=[inputs], outputs=[outputs])
    return model


@tf.function
def weight_clouds_more(image, mask, ratio=[1.0, 3.0]):
  # normalize the weights to sum to 1
  class_weights = tf.constant(ratio)
  class_weights = class_weights/tf.reduce_sum(class_weights)

  # make another mask, but one that has weights for every pixel
  weights = tf.gather(class_weights, indices=tf.cast(mask, tf.int32))
  return image, mask, weights



if __name__ == "__main__":
    
    # save the links for each of the 96 asset scenes
    links = get_asset_links()
    asset_links = write_links_to_file(links, fname='links.txt'):
    # download & extract assets (BE CAREFUL, TUNE HOW PARALLEL YOU WANT THIS)
    assets_dir = download_assets(asset_links, download_directory='assets')
    assets = extract(in_dir=assets_dir, out_dir=assets_dir)
    # make dataset consisting of the bands and mask for each asset
    ds = make_ds_from_assets(assets)

    # convenience args for parallel preprocessing
    parallelize = dict(num_parallel_calls=tf.data.AUTOTUNE, deterministic=False)
    
    # read in images and mask .TIF files
    ds = ds.map(read_img_and_mask, **parallelize)
    CARDINALITY = ds.cardinality()
    
    # take n random crops of size h, w
    n, h, w, c = 20, 128, 128, 3
    ds = ds.interleave(lambda img, mask: sample_crop(img, mask, h, w, n), **parallelize)
    # unstack the stacked image + mask into a tuple of image, mask
    ds = ds.map(lambda x: (x[:, :, 0:3], x[:, :, 3]), **parallelize)
    CARDINALITY *= n
    ds = ds.apply(tf.data.experimental.assert_cardinality(CARDINALITY))

    # weight clouds more in loss function, because high cost of false negatives
    ds = ds.map(weight_clouds_more, **parallelize)

    # shuffle, then construct 80-20 train-test split
    # use a batch size of 32, and 
    # prefetch to reduce time to max of preprocessing and ML, rather than sum
    ds = ds.shuffle(buffer_size=CARDINALITY)
    test_ds = ds.take(CARDINALITY // 5).prefetch(tf.data.AUTOTUNE).batch(32)
    train_ds = ds.skip(CARDINALITY // 5).prefetch(tf.data.AUTOTUNE).batch(32)

    # UNet Semantic Segmentation Architecture
    # see original paper here: https://arxiv.org/abs/1505.04597
    model = build_unet_segmentation_model(h, w, c)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    # train & save the best model from training
    os.system('mkdir saved_model') 
    history = model.fit(
      train_ds,
      validation_data=test_ds,
      epochs=50,
      callbacks=[tf.keras.callbacks.ModelCheckpoint(
                    'saved_model/cloud_model_checkpoint',
                     monitor="val_loss",
                     save_best_only=True,
                     save_freq="epoch")])
    
    # done! save model to disk
    print(model.evaluate(test_ds))
    model.save('saved_model/cloud_model_final')
