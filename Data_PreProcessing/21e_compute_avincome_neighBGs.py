# Computes neighbouring income from 2014 ACS data, using population-weighted averages. Based on 2010-2020 BG crosswalk.

import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import geopandas as geopds
from tqdm import tqdm
import matplotlib.pyplot as plt
import state_name_crs_mappings_ML as crsm
import us

# File path
root = ''
result_path = root + 'final_data/'
path_geodata = ''

# Income variable of interest
year = 2014
col_income = 'median_household_income_byBG_ACS' + str(year)

# List all states
states = []
for state in us.states.STATES:
    states +=[state.abbr]
states += ['DC']

len(states)

# Get socioeconomics per BG (output of 10b)
df_BG = pd.read_csv(result_path + '23_level_BG_US_imputedquantiles_20260504.csv')
df_BG.head(3)

# COnvert FIPS to string
df_BG['BGFP'] = df_BG['BGFP'].astype(str).str.zfill(12)
df_BG['STATEFP'] = df_BG['STATEFP'].astype(str).str.zfill(2)
df_BG['COUNTYFP'] = df_BG['COUNTYFP'].astype(str).str.zfill(5)

# Set index
df_BG.set_index('BGFP', inplace=True)

# Filter for relevant columns
df_socioecon = df_BG[['STATEFP','COUNTYFP',col_income,'total_pop_byBG']].copy()

# Compile dataset of neighboring bgs
distances = [10,50] # km
for d in distances:
    df_socioecon['av_income_'+str(d)+'km_withoutBG'] = np.nan
    df_socioecon['weighted_av_income_'+str(d)+'km_withoutBG'] = np.nan

# For loop
for state in []: # (states):
    print(state)
    if state == 'DC':
        fips = '11'
        state_name = 'District of Columbia'
    else:
        fips = us.states.lookup(state).fips
        state_name = us.states.lookup(fips).name
    df_socioecon_state = df_socioecon[df_socioecon['STATEFP'] == fips].copy()

    # Reproject to relevant metric system
    crs = crsm.us_state_to_crs[state_name]
    # gdf_states = gdf_states.to_crs(crs=crs)
    try:
        gdf_bg_inclnb = geopds.read_file(result_path + 'neighboring_bgs/tl_2020_'+fips+'_bg_neighbors.shp')
    except:
        # If there are no neighbours, there is no file (AK for instance)
        gdf_bg_inclnb = geopds.read_file(path_geodata + 'tl_bg/tl_2020_'+fips+'_bg/tl_2020_'+fips+'_bg.shp')
        print('No neighbours')
    # Change index
    assert len(gdf_bg_inclnb.GEOID.unique()) == len(gdf_bg_inclnb), 'GEOID not unique'
    gdf_bg_inclnb.set_index('GEOID',inplace=True)

    # Convert to cartesian
    gdf_bg_inclnb = gdf_bg_inclnb.to_crs(crs=crs)

    # Get BGs of state
    gdf_bg = gdf_bg_inclnb.loc[gdf_bg_inclnb['STATEFP'] == fips]

    # Iterate over CTs
    for BGFIPS in tqdm(gdf_bg.index):
        # Get CT of interest
        geometry_i = gdf_bg_inclnb['geometry'].loc[BGFIPS]
		
        for d in distances:
            # Get neighbouring areas
            ct_i_buffer = geometry_i.buffer(d*1000) # km
            gdf_ct_nb = gdf_bg_inclnb.clip(ct_i_buffer) # includes all BGs fully, which are somehow in the buffer

            # Average income in surrounding BGs
            # Filter for neighbouring BGs
            df_socioecon_i = df_socioecon.loc[df_socioecon.index.isin(gdf_ct_nb.index.to_list())] # based on all US data
                       
            # Reproducing av income without actual BG
            df_socioecon_i.drop(BGFIPS,axis=0,inplace=True)

            # Unweighted income
            df_socioecon_state.loc[BGFIPS,'av_'+str(year)+'_income_'+str(d)+'km_withoutBG'] = df_socioecon_i[col_income].mean()
            
            # Compute weighted nb income
            df_socioecon_state.loc[BGFIPS,'weighted_av_'+str(year)+'_income_'+str(d)+'km_withoutBG'] = (df_socioecon_i[col_income]*df_socioecon_i['total_pop_byBG']).sum()/df_socioecon_i['total_pop_byBG'].sum()
            
    # Save state data separately
    df_socioecon_state.to_csv(result_path + 'BGlevel/level_BG_'+state+'_wnbincome_R1.csv')

    # Save to US dataframe
    df_socioecon_US = pd.concat([df_socioecon_US, df_socioecon_state], axis=0)

# Compile US dataset and save
df_socioecon_US = pd.DataFrame()
for state in states:
    df_socioecon_state = pd.read_csv(result_path + 'BGlevel/level_BG_'+state+'_wnbincome_R1.csv', index_col=0)
    df_socioecon_US = pd.concat([df_socioecon_US, df_socioecon_state], axis=0)
df_socioecon_US = df_socioecon_US[['median_household_income_byBG_ACS2014','av_2014_income_10km_withoutBG','weighted_av_2014_income_10km_withoutBG','av_2014_income_50km_withoutBG','weighted_av_2014_income_50km_withoutBG']]
df_socioecon_US.index = df_socioecon_US.index.astype(str).str.zfill(12)
df_socioecon_US.to_csv(result_path + 'df_socioecon_US.csv')

# Merge onto BG_2020 and save
df_BG_US = df_BG.merge(df_socioecon_US, left_index=True, right_index=True, how='left')
df_BG_US.to_csv(result_path + '24_level_BG_US_wnbincome_20260504.csv')