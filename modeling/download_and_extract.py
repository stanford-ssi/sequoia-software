# Author: Yash Dalmia
# Date: Monday May 10, 2021

from bs4 import BeautifulSoup
import requests
import tarfile

import multiprocessing as mp
import concurrent.futures


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


def bands_and_mask(members):
    for file in members:  
        # only write what we actually need to disk
        if any(crit in file.name for crit in ["B2", "B3", "B4", "fixedmask"]):
            yield file


def download_and_extract(x):
    # read as a byte stream to avoid expensive disk IO
    # instead, we process in-memory
    r = requests.get(x, stream=True)
    tar = tarfile.open(fileobj=r.raw, mode='r|gz')
    tar.extractall(members=bands_and_mask(tar))
    tar.close()


# download and extract the 100GB of files in parallel

# online sources said cpu_cores + 1 is ideal for IO bound tasks
# but my microbenchmarks using plain mp.pool was only slightly slower
# using python's default number of threads however is much slower
links = get_asset_links()
with concurrent.futures.ThreadPoolExecutor(mp.cpu_count() + 1) as executor:
    executor.map(download_and_extract, links)

