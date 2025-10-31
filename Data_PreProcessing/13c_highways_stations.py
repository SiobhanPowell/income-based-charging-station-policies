################################
#
# Computes distance between stations and nearest highway
#
#################################
 
import os
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import geopandas as geopds
import us
import matplotlib.pyplot as plt
from tqdm import tqdm
from shapely import wkt
import re
import state_name_crs_mappings_ML as crsm
import time 

# Read data

# File path
root = ''
result_path = root + 'final_data/'
path_geodata = root + 'Data/geodata/'

# Check whether folder exists, if not create it
folder = result_path + 'stationlevel/'
if not os.path.exists(folder):
    os.makedirs(folder)

# Stations
df_stations = pd.read_csv(result_path + '00_alt_fuel_stations (Apr 3 2023)_wFIPS.csv',index_col=[0])
df_stations['STATEFP'] = df_stations['STATEFP'].astype(str).str.zfill(2)

# Read state shapefile
gdf_states = geopds.read_file(path_geodata + 'cb_2018_us_state_500k/cb_2018_us_state_500k.shp')

# Highways
file_hwy = path_geodata + 'tl_2022_us_primaryroads/tl_2022_us_primaryroads.shp'
gdf_hwy = geopds.read_file(file_hwy)

# states
states = []
for state in us.states.STATES:
    states +=[state.abbr]
states += ['DC']
print(states)

# Iterate
for state in states:
    # State characteristics
    print(state)
    if state == 'DC':
        fips = '11'
        state_name = 'District of Columbia'
    else:
        fips = us.states.lookup(state).fips
        state_name = us.states.lookup(state).name
    crs = int(crsm.state_to_crs(state_name).split(':')[1]) #crs = 2163
    gdf_states_i = gdf_states.loc[gdf_states['STUSPS'] == state]
    gdf_states_i = gdf_states_i.to_crs(epsg=crs)

    # Stations (needed as geofile for BG-merge)
    df_stations_state = df_stations.loc[df_stations['STATEFP'] == fips]
    gdf_stations_state = geopds.GeoDataFrame(df_stations_state, geometry=geopds.points_from_xy(df_stations_state.Longitude, df_stations_state.Latitude, crs="EPSG:4326"))
    gdf_stations_state = gdf_stations_state.to_crs(epsg=crs)
    gdf_stations_state = gdf_stations_state[['geometry']]
    
    # Primary

    # Convert
    gdf_hwy = gdf_hwy.to_crs(crs=crs)
    gdf_hwy_i = gdf_hwy.clip(gdf_states_i.buffer(500000)) # 500 km buffer

    # Assign
    assert gdf_hwy_i.crs == gdf_stations_state.crs, 'CRS hwy - stations do not match!'
    gdf_stations_state['nearest_highway_km'] = -1.
    for ind in tqdm(gdf_stations_state.index):
        geometry_i = gdf_stations_state['geometry'].loc[ind]
        gdf_stations_state['nearest_highway_km'].loc[ind] = np.round(gdf_hwy_i.distance(geometry_i).min()/1000.,3) # km

    # Secondary

    # Read original secondary file
    file_hwy2 = path_geodata + 'TIGER_secondaryroads_2022/tl_2022_'+fips+'_prisecroads.shp'
    gdf_hwy2 = geopds.read_file(file_hwy2)
    gdf_hwy2 = gdf_hwy2.to_crs(epsg=crs)
    
    # Which other states to load?
    try:
        gdf_bg_inclnb = geopds.read_file(result_path + 'neighboring_bgs/tl_2020_'+fips+'_bg_neighbors.shp')
    except:
        # If there are no neighbours, there is no file (AK for instance)
        gdf_bg_inclnb = geopds.read_file(path_geodata + 'tl_bg/tl_2020_'+fips+'_bg/tl_2020_'+fips+'_bg.shp')
        print('No neighbours')

    # Read other secondary files
    for state_nb in gdf_bg_inclnb['STATEFP'].unique():
        if state_nb != fips:
            # Read secondary hwy data
            file_hwy2 = path_geodata + 'TIGER_secondaryroads_2022/tl_2022_'+state_nb+'_prisecroads.shp'
            gdf_hwy2_nb = geopds.read_file(file_hwy2)
            gdf_hwy2_nb = gdf_hwy2_nb.to_crs(epsg=crs)
            
            # Merge
            assert gdf_hwy2.crs == gdf_hwy2_nb.crs, 'CRS do not match!'
            gdf_hwy2 = geopds.GeoDataFrame( pd.concat( [gdf_hwy2,gdf_hwy2_nb], ignore_index=True) , crs=gdf_hwy2.crs)

    # Clip
    gdf_hwy2_clipped = gdf_hwy2.clip(gdf_states_i.buffer(500000)) # 500 km buffer

    # Primary and secondary
    assert gdf_hwy2.crs == gdf_stations_state.crs, 'CRS hwy2 - stations do not match!'
    gdf_stations_state['nearest_primarysecondary_km'] = -1.
    gdf_stations_state['nearest_primarysecondary_km_UI'] = -1.
    gdf_hwy2_clipped_UI = gdf_hwy2_clipped.loc[gdf_hwy2_clipped['RTTYP'].isin(['U','I'])]
    for ind in tqdm(gdf_stations_state.index):
        geometry_i = gdf_stations_state['geometry'].loc[ind]
        gdf_stations_state['nearest_primarysecondary_km'].loc[ind] = np.round(gdf_hwy2_clipped.distance(geometry_i).min()/1000.,3) # km
        gdf_stations_state['nearest_primarysecondary_km_UI'].loc[ind] = np.round(gdf_hwy2_clipped_UI.distance(geometry_i).min()/1000.,3) # km

    # Save
    gdf_stations_state.drop('geometry',axis=1,inplace=True)
    gdf_stations_state.to_csv(result_path + 'stationlevel/level_stations_'+state+'_hwy.csv')