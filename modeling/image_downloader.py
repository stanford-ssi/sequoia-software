import os
import pandas as pd

# Downloads a list of images from a csv file
# Assumes web_scraper.py has been run

# Reads data values from CSV file
df = pd.read_csv('./data.csv')
# TODO: Don't rely on col names
scene_ids = df['Scene ID (Level-1T)'].values


for scene_id in scene_ids:
    filename = f"/data/scenes/{scene_id}.tar.gz"
    # Use OS utils to download and unpack images
    os.system(f"curl https://landsat.usgs.gov/cloud-validation/cca_l8/{scene_id}.tar.gz --output {filename}")
    os.system(f"tar -xzf {filename} -C /data/scenes")