from bs4 import BeautifulSoup
import requests
import pandas as pd

response = requests.get("https://landsat.usgs.gov/landsat-8-cloud-cover-assessment-validation-data");

if response.status_code != 200:
    print(f"ERROR: Request returned error code {response.status_code}")
    quit()

raw_data = response.text
soup = BeautifulSoup(raw_data, 'html.parser')
tables = soup.find_all('table')

# Initialize DF 
first_table = tables[2]
label_objs = first_table.tbody.tr.find_all('th')[1:]
labels = ['Biome']
labels.extend([x.strong.string for x in label_objs])
df = pd.DataFrame(columns = labels)

# Add every row from the website table to DF
tot_rows = 0
for table in tables[2:]:
    name = table.tbody.tr.th.strong.string
    rows = table.find_all('tr')
    for row in rows[1:]:
        cols = row.find_all('td')
        values = [name]
        for i, col in enumerate(cols[1:]):
            if i == 0:
                value = col.a.string
            else:
                value = col.string
            values.append(value)
        df.loc[tot_rows] = values
        tot_rows += 1

# Export to CSV
df.to_csv('./data.csv', index = False)

