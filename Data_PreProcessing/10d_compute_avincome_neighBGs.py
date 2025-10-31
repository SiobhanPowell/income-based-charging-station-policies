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
path_geodata = root + 'Data/geodata/'

# List all states
states = []
for state in us.states.STATES:
    states +=[state.abbr]
states += ['DC']

len(states)

# Get socioeconomics per BG (output of 10b)
df_socioecon = pd.read_csv(result_path + 'BGlevel/level_BG.csv')
df_socioecon.head(3)

# COnvert FIPS to string
df_socioecon['BGFP'] = df_socioecon['BGFP'].astype(str).str.zfill(12)
df_socioecon['STATEFP'] = df_socioecon['STATEFP'].astype(str).str.zfill(2)
df_socioecon['COUNTYFP'] = df_socioecon['COUNTYFP'].astype(str).str.zfill(5)

# Set index
df_socioecon.set_index('BGFP', inplace=True)

# Filter for relevant columns
df_socioecon = df_socioecon[['STATEFP','COUNTYFP','median_household_income_byBG','total_pop_byBG']].copy()

# Compile dataset of neighboring bgs
distances = [10,50] # km
for d in distances:
    df_socioecon['av_income_'+str(d)+'km'] = np.nan
    df_socioecon['av_income_'+str(d)+'km_withoutBG'] = np.nan
    df_socioecon['weighted_av_income_'+str(d)+'km_withoutBG'] = np.nan
    df_socioecon['av_income_'+str(d)+'km_imputed'] = np.nan
    df_socioecon['av_income_'+str(d)+'km_withoutBG_imputed'] = np.nan
    df_socioecon['weighted_av_income_'+str(d)+'km_withoutBG_imputed'] = np.nan

for state in (states): # 'TX'
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
    # gdf_bg_inclnb = geopds.read_file(path_geodata + 'tl_bg/tl_2020_'+fips+'_bg/tl_2020_'+fips+'_bg.shp')
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
            
            # Reproducing old data point
            # Save to state-specific socioecon dataframe
            df_socioecon_state.loc[BGFIPS,'av_income_'+str(d)+'km'] = df_socioecon_i['median_household_income_byBG'].mean()
            
            # Impute missing data (including actual BG)
            mean_income = df_socioecon_i.loc[~df_socioecon_i['median_household_income_byBG'].isna()]['median_household_income_byBG'].mean()
            df_socioecon_i['median_household_income_byBG_imputed'] = df_socioecon_i['median_household_income_byBG']
            df_socioecon_i.loc[df_socioecon_i['median_household_income_byBG_imputed'].isna(),'median_household_income_byBG_imputed'] = mean_income
            
            # Reproducing old datapoint with imputed data
            df_socioecon_state.loc[BGFIPS,'av_income_'+str(d)+'km_imputed'] = df_socioecon_i['median_household_income_byBG_imputed'].mean()
            
            # Reproducing av income without actual BG
            df_socioecon_i.drop(BGFIPS,axis=0,inplace=True)

            # Unweighted income
            df_socioecon_state.loc[BGFIPS,'av_income_'+str(d)+'km_withoutBG'] = df_socioecon_i['median_household_income_byBG'].mean()
            
            # Compute weighted nb income
            df_socioecon_state.loc[BGFIPS,'weighted_av_income_'+str(d)+'km_withoutBG'] = (df_socioecon_i['median_household_income_byBG']*df_socioecon_i['total_pop_byBG']).sum()/df_socioecon_i['total_pop_byBG'].sum()
            
            # Impute missing income data 
            df_socioecon_state.loc[BGFIPS,'av_income_'+str(d)+'km_withoutBG_imputed'] = df_socioecon_i['median_household_income_byBG_imputed'].mean()
            df_socioecon_state.loc[BGFIPS,'weighted_av_income_'+str(d)+'km_withoutBG_imputed'] = (df_socioecon_i['median_household_income_byBG_imputed']*df_socioecon_i['total_pop_byBG']).sum()/df_socioecon_i['total_pop_byBG'].sum()

    # Save state data separately
    df_socioecon_state.to_csv(result_path + 'BGlevel/level_BG_'+state+'_wnbincome.csv')