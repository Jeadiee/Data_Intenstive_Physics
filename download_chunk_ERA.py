""" This will allow us to define the chunks we want to donload from the ERA-5 datset"""

import ee
import csv
import sys
import os
import requests
import time

# Point to the Earth Engine project I created. 
ee.Initialize(project='datintensivephysics')

# Picks out the argument provided for chunk_ID. 
chunk_ID = int(sys.argv[1])

# Work dir that bp documentation recommends for data storage. (1Tb limit)
output_dir = '/user/work/uo23496/ERA5/'

# ERA5 variables chosen (see Onenote for this. Seem reasonable)
variables = [
    'temperature_2m',
    'dewpoint_temperature_2m',
    'total_precipitation_sum',
    'volumetric_soil_water_layer_1',
    'volumetric_soil_water_layer_2',
    'soil_temperature_level_1',
    'soil_temperature_level_2',
    'u_component_of_wind_10m',
    'v_component_of_wind_10m',
    'surface_latent_heat_flux_sum',
    'surface_net_solar_radiation_sum',
    'surface_net_thermal_radiation_sum',
    'surface_sensible_heat_flux_sum',
    'evaporation_from_bare_soil_sum',
    'evaporation_from_vegetation_transpiration_sum',
    'potential_evaporation_sum',
    'surface_sensible_heat_flux_min',
    'surface_sensible_heat_flux_max'
]

# Read the manifest file and get the chunk corresponding to the provided chunk_ID
# newline recommended from stack overflow to avoid issues with line endings in CSV files.
with open('manifest_ERA5.csv', newline ='') as csvfile:
    chunks = list(csv.DictReader(csvfile))

chunk = chunks[chunk_ID]

year = int(chunk['year'])
month = int(chunk['month'])
tile_id = int(chunk['tile_id'])

#  Get the filename from the chunk. this previously created slightly different filename in the manifest.
filename = chunk["filename"]

# Full path to the output file
output_path= os.path.join(output_dir, filename)

#logic to check for already downloaded files. 
if os.path.exists(output_path):
    print(f"File {output_path} already exists. Skipping download beep boop beep...")
    # partly unsure here but stack overflow suggests sys.exit(0) is a clean way to exit a script without error.
    sys.exit(0)

# Reconstruct monthly ERA5 image by using this fromYMD and advance method to get the start and end dates for the month.
start_date = ee.Date.fromYMD(year, month, 1)

# Finding the end date by advancing the start date by 1 month. This will be used to filter the ERA5 collection for the specific month.
end_date = start_date.advance(1, 'month')

# Collecing the ERA5 data based on what we define above. Can be modular. (Jack very much likes modular. Jack happy)
# Not defining the study area here as we define this in manifest. 
monthly_collection = (
    ee.ImageCollection('ECMWF/ERA5_LAND/DAILY_AGGR')   # daily aggregate (pre calculated, of data)
    .filterDate(start_date, end_date)
    .select(variables)
    .sort('system:time_start')   #go in order. Easier visuals for Jack.
)

# Red One gave me validation here that this is smart. Good enough for me
monthly_image = monthly_collection.toBands()

# Reconstruct geographical tile and segment based on chunk ID (This is where we make our loaf into breadcrumbs)
tile = ee.Geometry.Rectangle([
    float(chunk['xmin']),
    float(chunk['ymin']),
    float(chunk['xmax']),
    float(chunk['ymax'])
])

# Restrict download to Uruguay
countries = ee.FeatureCollection(
    'FAO/GAUL_SIMPLIFIED_500m/2015/level0'  # google recommends this as quicker if you don't need the full resolution (i.e coastal data). We don't.
)

uruguay = countries.filter(
    ee.Filter.eq('ADM0_NAME', 'Uruguay')
)

study_area = uruguay.geometry()

# Using 50m error margin to balance speed and accuracy. Prevents timeout. 100m is a good guess. 
download_region = tile.intersection(
    study_area, ee.ErrorMargin(100)
)

# Request direct download URL
params = {
    'name': filename.replace('.tif', ''),     # prevents double .tif in the filename.
    'region': download_region,
    'scale': 11132,                           # the standard number used for ERA5(something about 11132m per degree at the equator)
    'format': 'GEO_TIFF'                      # I have read that this is the best format for raster data. I also dont want a .zip file.
}

# try 3 times. 
for attempt in range(3):
    try:
        # Get the download URL and download the file
        url = monthly_image.getDownloadURL(params)
        # 300 second timeout to avoid timeout errors. This is a long download.
        response = requests.get(url, timeout=300)
        # raise an error if the request was unsuccessful
        response.raise_for_status()
        # Write the content to a file. 'wb' mode is used to write binary data, which is appropriate for image files.
        with open(output_path, 'wb') as file:
            file.write(response.content)

        print(f'Successfully downloaded!!!! {filename}. Beep boop beep...')
        break

    except Exception as error:
        print(f'Attempt {attempt + 1} failed: {error}')

        if attempt == 2:
            raise

        # wait 10 seconds before retrying.
        time.sleep(10)
