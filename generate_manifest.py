
import ee
import csv
import os
import calendar
from datetime import date

ee.Initialize(project='datintensivephysics')


# Define our study area as Uruguay using the FAO GAUL dataset


countries = ee.FeatureCollection(
    'FAO/GAUL_SIMPLIFIED_500m/2015/level0'
)

uruguay = countries.filter(
    ee.Filter.eq('ADM0_NAME', 'Uruguay')
)

study_area = uruguay.geometry()


# Define the download setting/
START_YEAR = 2001
END_YEAR = 2024

# Define the spatial tile size in degrees. This will be used to create a grid of tiles over the study area. 3 is seems reasonable for Uruguay. (Jack keeps things simple)
TILE_DEG = 3

OUTPUT_DIR = '/user/work/uo23496/ERA5/'

# name of the manifest file. 
MANIFEST_PATH = 'manifest.csv'

DATASET = 'ECMWF/ERA5_LAND/DAILY_AGGR'

# see comment in download_chunk.py for why I chose this scale. 
SCALE = 11132

VARIABLES = [
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

# Create the output directory if it doesn't exist. Protects my potentially poor directory naming. 
os.makedirs(OUTPUT_DIR, exist_ok=True)

if os.path.exists(MANIFEST_PATH):
    raise FileExistsError(
        f'{MANIFEST_PATH} already exists you silly goose. '
        'Move or rename it before generating a new manifest. We dont want to overwrite your precious data.'
    )

# Get the bounding box of the study area to define the spatial extent for tiling
bounds = study_area.bounds().coordinates().getInfo()[0]

min_lon = min(point[0] for point in bounds)
max_lon = max(point[0] for point in bounds)

min_lat = min(point[1] for point in bounds)
max_lat = max(point[1] for point in bounds)


# Generate spatial tiles based on the bounding box and TILE_DEG. This will create a grid of tiles over the study area. (Jack likes grids, they are neat and tidy) 
tiles = []

tile_id = 0

lon = min_lon

# here, we use a while loop to iterate over the longitude and latitude to create tiles. This is a simple way to create a grid of tiles over the study area. (Jack likes simple solutions)
while lon < max_lon:

    lat = min_lat

    while lat < max_lat:

        xmax = min(lon + TILE_DEG, max_lon)
        ymax = min(lat + TILE_DEG, max_lat)

        tile = ee.Geometry.Rectangle(
            [lon, lat, xmax, ymax]
        )

        # this allows us to check if the tile intersects with the study area. If it does, we add it to the list of tiles. (Jack likes to be thorough)
        intersects = study_area.intersects(
            tile,
            ee.ErrorMargin(100)
        ).getInfo()

        # keep it if it intersects. This is a simple way to create a grid of tiles over the study area.
        if intersects:
            tiles.append({
                'tile_id': tile_id,
                'xmin': lon,
                'ymin': lat,
                'xmax': xmax,
                'ymax': ymax
            })

            tile_id += 1

        # iterate over the latitude to create the next tile in the column
        lat += TILE_DEG
    # iterate over the longitude to create the next column of tiles
    lon += TILE_DEG

print(f'Generated {len(tiles)} spatial tiles. beep boop beep...')

# Red One asked us to define the manifest fields. This is a good idea. We will use this to track the download status of each chunk. (Jack likes to be organized)
fieldnames = [
    'chunk_id',
    'dataset',
    'year',
    'month',
    'start_date',
    'end_date',
    'expected_days',
    'variables',
    'tile_id',
    'xmin',
    'ymin',
    'xmax',
    'ymax',
    'scale',
    'filename',
    'status',
    'file_size_bytes',
    'checksum',
    'error'
]

# Now we will generate the manifest file. This will create a CSV file with the metadata for each chunk.
total_chunks = 0

with open(MANIFEST_PATH, 'w', newline='') as f:

    # dictwriter is a class that allows us to write dictionaries to a CSV file. We will use this to write the metadata for each chunk to the manifest file
    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    # allows us to create header row in csv file.
    writer.writeheader()

    for year in range(START_YEAR, END_YEAR + 1):

        for month in range(1, 13):

            start_date = date(year, month, 1)

            if month == 12:
                # if the month is December, we need to advance to the next year. 
                end_date = date(year + 1, 1, 1)
            else:
                # if not December, we can just advance to the next month. This is a simple way to get the end date for each month
                end_date = date(year, month + 1, 1)

            # checks if the number of days are correct. 
            expected_days = calendar.monthrange(
                year, month
            )[1]

            for tile in tiles:

                chunk_id = (
                    f'ERA5_{year}_{month:02d}_'
                    f'tile_{tile["tile_id"]:03d}'
                )

                filename = f'{chunk_id}.tif'

                writer.writerow({

                    'chunk_id': chunk_id,

                    'dataset': DATASET,

                    'year': year,
                    'month': month,

                    # istoformat() is standard for converting date to string. 
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),

                    'expected_days': expected_days,

                    'variables': ';'.join(VARIABLES),

                    'tile_id': tile['tile_id'],

                    'xmin': tile['xmin'],
                    'ymin': tile['ymin'],
                    'xmax': tile['xmax'],
                    'ymax': tile['ymax'],

                    'scale': SCALE,

                    'filename': filename,

                    'status': 'PENDING',

                    'file_size_bytes': '',
                    'checksum': '',
                    'error': ''

                })

                total_chunks += 1

print('\nManifest successfully generated.')

print(f'Years: {START_YEAR}-{END_YEAR}')
print(f'Months: {(END_YEAR - START_YEAR + 1) * 12}')
print(f'Spatial tiles: {len(tiles)}')
print(f'Total chunks: {total_chunks}')

print(f'Manifest: {MANIFEST_PATH}')
