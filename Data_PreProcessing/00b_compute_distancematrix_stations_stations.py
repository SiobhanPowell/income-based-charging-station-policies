################################
#
# Computes distance matrices between stations
#
#################################

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import geopandas as geopd
import us
import matplotlib.pyplot as plt
from tqdm import tqdm
import os 
import glob
import state_name_crs_mappings_ML as crsm
import time 

# Which states

# all
states = []
for state in us.states.STATES:
    states +=[state.abbr]
states += ['DC']

print(states)

# Relevant paths
root = ''
path = root + 'Data/'
result_path = root + 'final_data/'

# Read in charging station data

df_stations = pd.read_csv(result_path + '00_alt_fuel_stations (Apr 3 2023)_wFIPS.csv',index_col='unique_ID') # added _prepred on 06/29/2024

# Create directory if not exists
if not os.path.exists(result_path + 'distancematrices_stations_uniqueID/'):
	os.makedirs(result_path + 'distancematrices_stations_uniqueID/')

# Calculate distance matrices for each state

for state in states:
	print(state)

	# Get suitable crs
	crs = int(crsm.state_to_crs(crsm.abbrev_to_state(state)).split(':')[1]) #2163
	if state == 'DC':
		fips = '11'
	else:
		state_fips = us.states.lookup(state).fips

	# Filter for state
	df_stations_state = df_stations.loc[df_stations['State'] == state]

	# Convert to geofile
	gdf_stations_state = geopd.GeoDataFrame(df_stations_state, geometry=geopd.points_from_xy(df_stations_state.Longitude, df_stations_state.Latitude, crs="EPSG:4326"))
	gdf_stations_state = gdf_stations_state.to_crs(epsg=crs)
	gdf_stations_state = gdf_stations_state[['Station Name','geometry']]

	# Establish distance matrix for distance histogram
	df_distance_matrix = pd.DataFrame(index=gdf_stations_state.index,columns=gdf_stations_state.index,data=np.nan)

	# Get distances
	for ind in tqdm(gdf_stations_state.index):

		# Calculate distance of one charging station to PoIs
		geometry_i = gdf_stations_state['geometry'].loc[ind]
		gdf_stations_state['distance_i'] = gdf_stations_state.distance(geometry_i)
		df_distance_matrix[ind] = gdf_stations_state['distance_i']

	# Save
	df_distance_matrix.to_csv(result_path + 'distancematrices_stations_uniqueID/' + state + '_stations_distancematrix.csv')



