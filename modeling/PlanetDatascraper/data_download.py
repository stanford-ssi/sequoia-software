"""
CS230
Grant Regen
Planet API Scraping Script
May 2020
"""

import numpy as np
import os
import sys
import json
import requests
import geojsonio
import time
from multiprocessing.dummy import Pool as ThreadPool
from retrying import retry
import pdb
from PIL import Image
import gdal
import subprocess

"""
User Global Inputs:
"""

"""
Instructions: Array of locations
"""
# is this a negative image without an object:
negative_image = False

locations = [[-104.847, 39.634], [-105.065, 39.544], [-104.663, 39.612], [-106.78, 39.36], [-104.606, 38.262],
             [-104.764, 38.264], [-105.699, 38.592]]

location_labels = ["cherry creek state park", "chatfield state park", "aurora reservoir", "ruedi reservoir", "pueblo",
                   "lake pueblo state park", "waugh mountain"]

"""
Instructions: Fill in personal API Key
"""
PLANET_API_KEY = "185c76df022f42ce964cf826d5ca3730"  # personal Planet API acess key

"""
Instructions: choose number of images desired to activate and download -- if going too slow increase multiprocessing chains number
"""
number_images = True  # number images to download from id set OR True to download all images (after 150, just use True)
number_multiprocessing = 30  # keep less than half of number_images when large image batches

image_width_height = 256
square_split_ratio = 1  # splits image into this many square images
redo_id_search = True  # reload all image ids -- clears all past ids

"""
Instructions: uncomment one image type and the corresponding square_split_ratio for the desired sat data.
"""
# IMAGE TYPE
# Recomendations for image splitting based on instrument and instrument selection
# item_types = ["Landsat8L1G"] #landsat
# square_split_ratio = 10
# item_types = ["PSScene3Band"] #Planet Scope Dove
# square_split_ratio = 5
item_types = ["REOrthoTile"]  # Rapid Eye
square_split_ratio = 8
# item_types = ["Sentinel2L1C"] #setinel2
# square_split_ratio = 9

# do not use for now
####item_types = ["SkySatCollect"] #SkySat
####square_split_ratio = 7


"""
Instructions: fill in path for own computer -- program will make folder if specified...
"""
path_and_name_of_id_list = '/Users/flynn/cs230/planet/data/batch2/image_ids.txt'
path_and_name_json_list = '/Users/flynn/cs230/planet/data/batch2/id_coordinates.txt'
path_image_folder = '/Users/flynn/cs230/planet/data/batch2/images/'

if not os.path.exists(path_image_folder):
    os.makedirs(path_image_folder)

###Filters:

"""
Instructions: Filters --- change date data to desired range (some dates are older than sat coverage)
"""
date_filter = {
    "type": "DateRangeFilter",  # Type of filter -> Date Range
    "field_name": "acquired",  # The field to filter on: "acquired" -> Date on which the "image was taken"
    "config": {
        "gte": "2017-01-05T00:00:00.000Z",  # "gte" -> Greater than or equal to
        "lte": "2017-12-25T00:00:00.000Z"  # "lte" -> Less than or equal to
    }
}


def construct_geometry_filter(filter_type, coords):
    """
    :param filter_type: determine whether the Point or Polygon filter is desired
    :param coords: either a list of two coordinates, or a list of lists of two coordinates
    :return: a geojson geometry filter
    """
    filter = {
        "type": "GeometryFilter",
        "field_name": "geometry",
        "config": {
            "type": filter_type,
            "coordinates": coords
        }
    }
    return filter


geo_filter_list = []

for coords in locations:
    geo_filter_list.append(construct_geometry_filter(filter_type="Point", coords=coords))

"""
Instructions: Filters --- change geometry data
"""

geometry_filter_california = {
    "type": "GeometryFilter",
    "field_name": "geometry",
    "config": {
        "type": "Point",
        "coordinates": [-109.00, 40.85]

        # "type": "Polygon",
        # "coordinates": [
        # [
        # [-109.00, 40.85],
        # [-108.98, 40.85],
        # [-108.98, 40.83],
        # [-109.01, 40.83]
        # ]
        # ]
    }
}

"""
Instructions: Filters --- cloud cover
"""
cloud_cover = {
    "type": "RangeFilter",
    "field_name": "cloud_cover",
    "config": {
        "lte": 0.4
    }
}

or_filter = {
    "type": "OrFilter",
    "config": []
}

or_filter["config"].extend(geo_filter_list)

# merge desired filters with AND filter
and_filter = {
    "type": "AndFilter",
    "config": [date_filter, cloud_cover, or_filter]
}

"""
End of User Inputs.
"""

""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""

# global required values for mulitprocessing--do not alter
session = requests.Session()
visual_location_url = []


def main():
    print("\nSTARTING PLANET SCRIPT...\n")

    # submit specified request

    Trial = {
        "name": "Trial",
        "item_types": item_types,
        "interval": "day",
        "filter": and_filter
    }

    # begin and authenticate session
    session.auth = (PLANET_API_KEY, "")
    if (redo_id_search):
        # create a saved search with filters specified
        saved_search = session.post(
            'https://api.planet.com/data/v1/searches/',
            json=Trial)
        saved_search_id = saved_search.json()["id"]

        # save first page of search
        first_page = ("https://api.planet.com/data/v1/searches/{}" +
                      "/results?_page_size={}").format(saved_search_id, 200)

        # print and store all filtered feature ids
        saved_ids = []
        saved_json = []
        fetch_page(first_page, session, saved_ids, saved_json)
        print("Finshed getting IDs")
        print("Saving list to file...")
        if os.path.exists(path_and_name_of_id_list):  # clear current list if exists
            os.remove(path_and_name_of_id_list)
        with open(path_and_name_of_id_list, 'w') as f:
            for item in saved_ids:
                f.write("%s\n" % item)
        if os.path.exists(path_and_name_json_list):  # clear current list if exists
            os.remove(path_and_name_json_list)
        with open(path_and_name_json_list, 'w') as f:
            for i in range(len(saved_json)):
                json.dump(saved_json[i], f)
        print("Finshed saving ID's to text file...")

    # create multiple threads for faster api activation
    parallelism = number_multiprocessing
    thread_pool = ThreadPool(parallelism)

    print("Creating truncated array for activation...")

    with open(path_and_name_of_id_list) as f:
        if (number_images == True):
            item_ids = f.read().splitlines()[:]  # only grab specified amount of images
        else:
            item_ids = f.read().splitlines()[:number_images]  # only grab specified amount of images

    print("Begining Multiprocessing feature activation...")
    thread_pool.map(activate_item, item_ids)

    print("\nAll visuals have been activated for download...\n")

    # pdb.set_trace()
    for i in range(len(visual_location_url)):
        pl_download(visual_location_url[i], i, saved_json)
        print("image download completed")

    print("FINISHED :)\n")


###Helper Functions:

"""
Function to download asset files
Parameters:
 - url (the location url)
 - filename (the filename to save it as. defaults to whatever the file is called originally)
"""


def pl_download(url, index, saved_json, filename=None):
    # Send a GET request to the provided location url, using your API Key for authentication
    res = requests.get(url, stream=True, auth=(PLANET_API_KEY, ""))
    # If no filename argument is given
    if not filename:
        # Construct a filename from the API response
        if "content-disposition" in res.headers:
            filename = res.headers["content-disposition"].split("filename=")[-1].strip("'\"")
        # Construct a filename from the location url
        else:
            filename = url.split("=")[1][:3]
    # Save the file
    with open(path_image_folder + filename, "wb") as f:
        for chunk in res.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
        if (filename != 'eyJ'):
            src_path = path_image_folder + filename
            """
            Cut image into grid with interpolated high-quality coordinate calculation
            """
            ds = gdal.Open(src_path)
            gt = ds.GetGeoTransform()
            width_px = ds.RasterXSize
            height_px = ds.RasterYSize
            # Get coords for lower left corner
            xmin = int(gt[0])
            xmax = int(gt[0] + (gt[1] * width_px))
            # get coords for upper right corner
            if gt[5] > 0:
                ymin = int(gt[3] - (gt[5] * height_px))
            else:
                ymin = int(gt[3] + (gt[5] * height_px))
            ymax = int(gt[3])
            tile_width = (xmax - xmin) // square_split_ratio  # 4000
            tile_height = tile_width
            for x in range(xmin, xmax, tile_width):
                for y in range(ymin, ymax, tile_height):
                    file_name = src_path[:-3] + '_{}_{}.tif'.format(x, y)
                    if (not os.path.exists(file_name)):
                        gdalwarp('-te', str(x), str(y), str(x + tile_width),
                                 str(y + tile_height), '-multi', '-wo', 'NUM_THREADS=ALL_CPUS',
                                 '-wm', '500', src_path, file_name)

                    im = Image.open(file_name)
                    # check square for empty pixels--eliminate these squares
                    if (not (np.all(np.asarray(im.split()[-1])))):
                        os.remove(file_name)
                    else:
                        ## save square json info in txt file
                        info = saved_json[index]
                        data = gdal.Open(file_name)
                        info['geometry'] = [gdal.Info(data, format='json')['wgs84Extent'],
                                            gdal.Info(data, format='json')['cornerCoordinates']]

                        corners = gdal.Info(data, format='json')['wgs84Extent']['coordinates'][0]
                        # pdb.set_trace()
                        # save image as jpg
                        if (not negative_image):
                            name_index = 0
                            for location in locations:
                                if ((abs(location[0]) < abs(corners[0][0])) and (
                                        abs(location[0]) > abs(corners[2][0])) and
                                        (abs(location[1]) < abs(corners[0][1])) and (
                                                abs(location[1]) > abs(corners[2][1]))):
                                    ##resize image for deep learning
                                    im = im.resize((image_width_height, image_width_height), Image.LANCZOS)
                                    im = im.convert("RGB")
                                    im.save(file_name[:-4] + '_' + location_labels[name_index] + '.jpg', "JPEG",
                                            quality=100)

                                    with open(file_name[:-4] + '_' + location_labels[name_index] + "_data.txt",
                                              'w') as f:
                                        json.dump(info, f)
                                name_index += 1
                                # save empty text file for negative results
                        else:
                            ##resize image for deep learning
                            im = im.resize((image_width_height, image_width_height), Image.LANCZOS)
                            im = im.convert("RGB")
                            im.save(file_name[:-3] + 'jpg', "JPEG", quality=100)
                            with open(file_name[:-4] + "_data.txt", 'w') as f:
                                json.dump(info, f)
                            with open(file_name[:-3] + "txt", 'w') as fp:
                                fp.write("0")
                                fp.close()

                        # remove tiff file
                        os.remove(file_name)
        os.remove(path_image_folder + filename)
    return filename


"""
Pretty print JSON object
"""


def p(data):
    print(json.dumps(data, indent=2))


"""
Print out ID labels for each feature on page
"""


def handle_page(page, saved_ids, saved_json):
    for item in page["features"]:
        print(item["id"])
        saved_ids.append(item["id"])
        saved_json.append(item)
        """
        long = 0.
        lat = 0.
        for i in range(4):
            long += item["geometry"]["coordinates"][0][i][0]
            lat += item["geometry"]["coordinates"][0][i][1]
        long /= 4.
        lat /= 4.
        time = item["properties"]["acquired"]
        sat_id = item["properties"]["satellite_id"]
        saved_coordinates.append([long,lat,time,sat_id])
        """


"""
Run through all pages of large search
How to Paginate:
1) Request a page of search results
2) do something with the page of results
3) if there is more data, recurse and call this method on the next page.
"""


def fetch_page(search_url, session, saved_ids, saved_json):
    page = session.get(search_url).json()
    handle_page(page, saved_ids, saved_json)
    next_url = page["_links"].get("_next")
    if next_url:
        fetch_page(next_url, session, saved_ids, saved_json)


"""
Activate item from api with rate limiting
Only activates first item type of specificed
items list -- will update later to modify this
"""


# "Wait 2^x * 1000 milliseconds between each retry, up to 10
# seconds, then 10 seconds afterwards"
@retry(
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000)
def activate_item(item_id):
    print("attempting to activate: " + item_id)
    # request an item
    item = session.get(
        ("https://api.planet.com/data/v1/item-types/" +
         "{}/items/{}/assets/").format(item_types[0], item_id))
    # pdb.set_trace()

    if item.status_code == 404:
        print("Item not found...Critical error" + item_id)
        raise Exception("ERROR 404, not found")

    if item.status_code == 202:
        print("Item currently being activated..." + item_id)
        raise Exception("Currently being activated, give time to download")

    # raise an exception to trigger the retry
    if item.status_code == 429:
        raise Exception("rate limit error")

    if item.status_code == 403:
        print("Acess to activation denied..." + item_id)
        raise Exception("Retry, acess denied")

    # request activation
    result = session.post(item.json()["visual"]["_links"]["activate"])
    print(str(item_id) + " " + str(result.status_code))

    if result.status_code == 429:
        raise Exception("rate limit error")

    if result.status_code == 403:
        print("Acess to activation denied...check account permissions " + item_id)
        raise Exception("Retry, acess denied")

    # p(item.json()["visual"])
    # pdb.set_trace()
    visual_location_url.append(item.json()["visual"]["location"])
    print("activation succeeded for item " + item_id)
    print("Item added to item list for download " + item_id)


def gdalwarp(*args):
    return subprocess.check_call(['gdalwarp'] + list(args))


if __name__ == '__main__':
    main()
