################################
#
# Computes distance from BGs to highways
#
#################################

import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import geopandas as geopds
from tqdm import tqdm
import matplotlib.pyplot as plt
import state_name_crs_mappings_ML as crsm
import us

# Read data

# File path
root = ''
result_path = root + 'final_data/'
path_geodata = root + 'Data/geodata/'

# Read state shapefile
gdf_states = geopds.read_file(path_geodata + 'cb_2018_us_state_500k/cb_2018_us_state_500k.shp')

# Highways
file_hwy = path_geodata + 'tl_2019_us_primaryroads/tl_2019_us_primaryroads.shp'
gdf_hwy = geopds.read_file(file_hwy)

# states
states = []
for state in us.states.STATES:
    states +=[state.abbr]
states += ['DC']
print(states)

# Iterate
for state in tqdm(states):
    print(state)
    crs_cart = int(crsm.state_to_crs(crsm.abbrev_to_state(state)).split(':')[1]) #crs = 2163

    # BG shapefile
    if state == 'DC':
        fips = '11'
    else:
        fips = us.states.lookup(state).fips
    file_bg = path_geodata + 'tl_bg/tl_2020_'+fips+'_bg/tl_2020_'+fips+'_bg.shp'
    gdf_bg = geopds.read_file(file_bg)
    df_bg = gdf_bg[['GEOID','geometry']]
    df_bg.rename(columns={'GEOID':'BGFIPS'},inplace=True)
    df_bg = df_bg.to_crs(crs=crs_cart)

    # Re-project
    gdf_hwy = gdf_hwy.to_crs(crs=crs_cart)
    gdf_states_i = gdf_states.loc[gdf_states['STUSPS'] == state]
    gdf_states_i = gdf_states_i.to_crs(crs=crs_cart)
    # gdf_hwy_i = gdf_hwy.clip(gdf_states_i.buffer(500000)) # 500 km buffer
    gdf_hwy_i = gdf_hwy.clip(gdf_states_i)

    # Assign distances to highways
    df_bg['nearest_highway_km_BG'] = -1.
    for ind in tqdm(gdf_bg.index):
        geometry_i = df_bg['geometry'].loc[ind]
        df_bg.loc[ind,'nearest_highway_km_BG'] = np.round(gdf_hwy_i.distance(geometry_i).min()/1000.,3) # km
			
    # Save
    df_bg.drop('geometry',axis=1,inplace=True)
    df_bg.to_csv(result_path + 'BGlevel/level_bg_'+state +'_hwy.csv')