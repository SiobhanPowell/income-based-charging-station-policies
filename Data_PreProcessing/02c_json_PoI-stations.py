#!/usr/bin/env python
# coding: utf-8

################################
#
# This code takes pre-compiled data as an input.
# On a station-level basis, it filters the 10 nearest PoI within 5000 meters of a station.
#
#################################

# Import

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import us
from tqdm import tqdm
import os 
import state_name_crs_mappings_ML as crsm
import geopandas as geopd
import json

# Path

root = ''
path = root + 'Data/'
path_US_data = root + 'Data/geodata/'
result_path = root + 'final_data/'
path_IRA = root + 'Data/IRA/1.0-shapefile-codebook/usa/'

# Check if output folders exist, otherwise create

if not os.path.exists(result_path + '10neareststations_PoI_uniqueID_within_5000m/'):
    os.makedirs(result_path + '10neareststations_PoI_uniqueID_within_5000m/')
if not os.path.exists(result_path + 'stations_PoI_uniqueID_within_500m/'):
    os.makedirs(result_path + 'stations_PoI_uniqueID_within_500m/')

# Functions

# Split number of columns for sequential read-in if data size is large
def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

# Which states

states = []
for state in us.states.STATES:
    states +=[state.abbr]
states += ['DC']

print(states)

# County shapefile

gdf_county = geopd.read_file(path + 'geodata/tl_2022_us_county/tl_2022_us_county.shp')
gdf_county['COUNTYFP'] = gdf_county['STATEFP'] + gdf_county['COUNTYFP']

# Read in charging station data as created by 00_prepare_stations.ipynb

df_stations = pd.read_csv(result_path + '00_alt_fuel_stations (Apr 3 2023)_wFIPS.csv',index_col='unique_ID',dtype={'STATEFP':str,'COUNTYFP':str})

# Iterate over states

for state in states:
    print(state)

    # Get correct crs and FIPS
    crs = int(crsm.state_to_crs(crsm.abbrev_to_state(state)).split(':')[1]) #2163
    if state == 'DC':
        state_fips = '11'
    else:
        state_fips = us.states.lookup(state).fips
    
    # Iterate over counties
    dict_stations_5000 = dict() # to store 10 nearest within 5000m
    dict_stations_500 = dict() # to store all PoI within 500m
    for county in tqdm(sorted(set(gdf_county['COUNTYFP'].loc[gdf_county['STATEFP'] == state_fips]))):

        # Get charging stations for column selection (actually only needed for CA)
        gdf_stations_state_county = df_stations.loc[df_stations['COUNTYFP'] == county]
        
        # Read distance matrix
        col_stations = [str(i) for i in gdf_stations_state_county.index.to_list()]
        if os.stat(result_path + 'distancematrices_uniqueID/'+state+'_' + county + '_distancematrix.csv').st_size < 10090320531:
            list_col_stations = [col_stations]
        else:
            list_col_stations = list(split(col_stations,3)) # Split into 3 parts for sequential read-in
        
        # Sequential read-in
        for usecols in list_col_stations:
            try:
                df_distance_matrix = pd.read_csv(result_path + 'distancematrices_uniqueID/'+state+'_' + county + '_distancematrix.csv',index_col=['placekey'],usecols=['placekey']+usecols)
            except BaseException as exp:
                import sys; sys.exit('Error in reading distance matrix')

            # Iterate over stations
            for ind in usecols: #tqdm(gdf_stations_state_county.index):
                # Get list of stations within 5000
                df = df_distance_matrix.loc[df_distance_matrix[str(ind)] <= 5000]
                df.sort_values(by=str(ind),ascending=True,inplace=True)
                list_poi_nearby_5000 = df.index[:10].to_list()
                dict_stations_5000[ind] = list_poi_nearby_5000
                # Get list of stations within 500 
                df = df_distance_matrix.loc[df_distance_matrix[str(ind)] <= 500]
                df.sort_values(by=str(ind),ascending=True,inplace=True)
                list_poi_nearby_500 = df.index.to_list()
                dict_stations_500[ind] = list_poi_nearby_500

    # Save to json
    json_name_5000 = result_path + '10neareststations_PoI_uniqueID_within_5000m/'+state+'_5000.json'
    with open(json_name_5000, 'w') as fp:
        json.dump(dict_stations_5000, fp,indent=2)
    json_name_500 = result_path + 'stations_PoI_uniqueID_within_500m/'+state+'_500.json'
    with open(json_name_500, 'w') as fp:
        json.dump(dict_stations_500, fp,indent=2)