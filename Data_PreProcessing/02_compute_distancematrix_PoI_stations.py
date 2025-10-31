#!/usr/bin/env python
# coding: utf-8

################################
#
# This code takes Dewey data and AFDC station data as an input.
# It calculates the distance matrix between all stations and PoI (within each county).
# It saves the number of PoI nearby each station by radius for an overview.
#
#################################

# Import

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import geopandas as geopd
import us
import matplotlib.pyplot as plt
from tqdm import tqdm
import os 
import time 
import state_name_crs_mappings_ML as crsm

# Which states

# all
states = []
for state in us.states.STATES:
    states +=[state.abbr]
states += ['DC']

print(states)

# Specify parameters

root = ''
path = root + 'Data/'
path_US_data = root + 'Data/geodata/'
result_path = root + 'final_data/'
path_IRA = root + 'Data/IRA/1.0-shapefile-codebook/usa/'

# Check whether output folder exists, otherwise create

if not os.path.exists(result_path + 'distancematrices_uniqueID/'):
    os.makedirs(result_path + 'distancematrices_uniqueID/')

# Read in county shapefile as ground truth for all states

gdf_county = geopd.read_file(path + 'geodata/tl_2022_us_county/tl_2022_us_county.shp')
gdf_county['COUNTYFP'] = gdf_county['STATEFP'] + gdf_county['COUNTYFP']

# Read in charging station data as created by 00_prepare_stations.ipynb

df_stations = pd.read_csv(result_path + '00_alt_fuel_stations (Apr 3 2023)_wFIPS.csv',index_col='unique_ID',dtype={'STATEFP':str,'COUNTYFP':str})

# Create distance matrices

for state in states:
    print(state)

    # Get correct crs and FIPS
    crs = int(crsm.state_to_crs(crsm.abbrev_to_state(state)).split(':')[1]) #2163
    if state == 'DC':
        state_fips = '11'
    else:
        state_fips = us.states.lookup(state).fips

    # gdf_county = gdf_county.to_crs(epsg=crs)
    
    # Read in all PoI by state (result of 01b_split_PoI_bystate.ipynb)

    file = result_path + 'Dewey/01_compiled_' + state + '.csv'
    df_dewey_state = pd.read_csv(file,index_col=['placekey'],dtype={'STATEFP':str,'COUNTYFP':str})
    print('Number of PoIs: '+str(len(df_dewey_state)))

    # Convert to geodataframe

    gdf_dewey_state = geopd.GeoDataFrame(
        df_dewey_state, geometry=geopd.points_from_xy(df_dewey_state.longitude, df_dewey_state.latitude), crs="EPSG:4326")
    gdf_dewey_state = gdf_dewey_state.to_crs(epsg=crs)
    gdf_dewey_state['COUNTYFP'] = gdf_dewey_state['COUNTYFP'].str.zfill(5)

    # # Charging stations

    df_stations_state = df_stations.loc[df_stations['State'] == state]
    print('Number of stations in '+state+': '+str(len(df_stations_state)))

    # Convert to geodataframe

    gdf_stations_state = geopd.GeoDataFrame(df_stations_state, geometry=geopd.points_from_xy(df_stations_state.Longitude, df_stations_state.Latitude, crs="EPSG:4326"))
    gdf_stations_state = gdf_stations_state[['COUNTYFP','geometry']]
    gdf_stations_state['COUNTYFP'] = gdf_stations_state['COUNTYFP'].str.zfill(5)
    gdf_stations_state = gdf_stations_state.to_crs(epsg=crs)

    if gdf_stations_state.crs != gdf_dewey_state.crs:
        import sys; sys.exit('Error: Stations and PoI crs do not match')

    # Calculate distance matrix by county: station x PoI
    # This is only needed once for different radii

    for county in tqdm(sorted(set(gdf_county['COUNTYFP'].loc[gdf_county['STATEFP'] == state_fips]))):

        # Use this if process got stuck within a state for a given county
        if True: # int(county) >= 6035:
            print(county)

            # Filter for county to facilitate faster merge
            gdf_stations_state_county = gdf_stations_state.loc[gdf_stations_state['COUNTYFP'] == county]
            gdf_dewey_state_FIPS_county = gdf_dewey_state.loc[gdf_dewey_state['COUNTYFP'] == county]

            # Establish distance matrix : unique_ID X placekey
            df_distance_matrix = pd.DataFrame(index=gdf_dewey_state_FIPS_county.index,columns=gdf_stations_state_county.index,data=np.nan)
            
            for ind in (gdf_stations_state_county.index):

                # Calculate distance of one charging station to PoIs
                geometry_i = gdf_stations_state_county['geometry'].loc[ind]
                gdf_dewey_state_FIPS_county['distance_i'] = gdf_dewey_state_FIPS_county.distance(geometry_i)#.m
                df_distance_matrix[ind] = gdf_dewey_state_FIPS_county['distance_i']

            # Save info
            df_distance_matrix.to_csv(result_path + 'distancematrices_uniqueID/'+state+'_' + county + '_distancematrix.csv')
            time.sleep(5)