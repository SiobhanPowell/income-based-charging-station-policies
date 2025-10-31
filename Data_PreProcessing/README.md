# Data compilation

The code in Data_PreProcessing uses data from AFDC, Safegraph data provided by Dewey, and other relevant sources to create station- and BG-level datasets for the anaylsis.

## 0*: Preparation of original data

00_prepare_stations.py: 
- Input: alt_fuel_stations (Apr 3 2023).csv (AFDC), TIGER shapefiles
- Takes all charging stations and creates UID. UID will be used in distance matrices etc.
- Excludes stations which are not within the US. Excludes Canadian provinces and Puerto Rico.
- Assigns FIPS codes (state to BG level)
- Output: 00_alt_fuel_stations (Apr 3 2023)_wFIPS.shp, 00_alt_fuel_stations (Apr 3 2023)_wFIPS.csv

00b_compute_distancematrix_stations_stations.py:
- Input: 00_alt_fuel_stations (Apr 3 2023)_wFIPS.csv
- Filters stations by state and creates geofile
- Computes distance [km] between stations within each state
- Output: distancematrices_stations_uniqueID/' + state + '_stations_distancematrix.csv

01_compile_PoIs.ipynb (SP):
- Input: Safegraph PoI data (core_poi-geometry-part'+str(file_number)+'.csv)
- Combine with files of MP
- Output: Single file of PoIs (compiled.csv)

01b_split_PoI_bystate.ipynb:
- Input: Full list of PoIs (compiled.csv)
- Split by US state
- Remove charging stations from list of PoIs to avoid double accounting
- Assign FIPS codes to each PoI
- Output: List of PoIs by state (compiled_'+state+'.csv), list of PoIs by state with FIPS (01_compiled_'+state+'.csv)

02_compute_distancematrix_PoI_stations.py:
- Input: List of stations (00_alt_fuel_stations (Apr 3 2023)_wFIPS.csv) and list of PoIs (01_compiled_' + state + '.csv)
- Calculate distance matrix by county: station x PoI
- Output: state+'_' + county + '_distancematrix.csv

02c_json_PoI-stations.py:
- Input: Station data (00_alt_fuel_stations (Apr 3 2023)_wFIPS.csv) and PoI-station distance matrices (state+'_' + county + '_distancematrix.csv)
- Finds all PoI within 500m of a station (Output: 10neareststations_PoI_uniqueID_within_500m/'+state+'_500.json)
- Finds ten nearest PoI within 5000m of a s tation (Output: 10neareststations_PoI_uniqueID_within_5000m/'+state+'_5000.json)
- Both needed for mobility data assignment

03_compile_patternsdata.py:
- Input: Full list of POI (compiled.csv)
- Assigns mobility data/patterns to POIs
- Output: POIs with patterns (compiled_plus_patterns)

03b_SafeGraph_patterns_near_stations.ipynb:
- Input: List of POIs with patterns (compiled_patterns.csv) and stations (00_alt_fuel_stations (Apr 3 2023)_wFIPS.csv)
- Loads the compiled patterns data, station list, and json files of the nearby POIs to each station
- Calculates the average patterns for nearby POIs to each station
- Output: patternsonly_uniqueID_'+savedate+'.csv

04_write_category_groupings.ipynb:
- Input: compiled.csv
- Prepares list of PoI top categories as Excel
- Reads in manually adjusted file (top_categories_classification_final.csv) to create category groupings module
- Output: category_groupings.py

04b_add_info_PoI.ipynb:
- Input: PoIs by state (01_compiled_'+state+'.csv') and category groupings module (category_groupings_250403)
- Add consolidates top categories to PoIs
- Output: 04b_compiled_'+state+'_addinfo.csv

## 1*: Prepare BG-level dataset

### Assemble BG-level socioeconomics

10_assemble_socioeconomicdata.ipynb:
- Input: Safegraph CENSUS data
- Use selected data and compile to BG-level dataset of socioeconomics
- Normalize relevant columns
- Compute additional variable
- Output: CENSUS_selected_cols_EV.csv

10b_combine_BGs_socioeconomics.ipynb:
- Input: CENSUS_selected_cols_EV.csv an TIGER BG shapefiles (tl_2020_'+fips+'_bg.shp)
- Compute Moran's i and Gini coefficients
- Output: level_BG.csv

10c_prepare_includeavincome_neighBGs.ipynb:
- Input: level_BG.csv and TIGER shapefiles
- Create state and BG shapefiles with 100km buffer aroud state boundaries
- Calculate neighboring income
- Output: level_BG_wnbincome.csv

10d_compute_avincome_neighBGs.py:
- Input: BG-level socioeconomic data level_BG.csv
- Select neighboring BGs within 10km and 50km
- Compute different measures of weighted neighboring income
- Output: level_BG_'+state+'_wnbincome.csv

10f_compile_IRA.ipynb:
- BG and IRA shapefiles
- Output: level_BG_'+state+'_IRA.csv (whether BGs are disadvantaged) and level_BG_'+state+'_nbIRA.csv (share of disadvantaged BGs surrounding a BG)

### Prepare county-level

11_compile_countylevel.ipynb:
- Input: Shapefiles
- Add population density, number of cars (Safegraph CENSUS)
- Output: level_county.csv

### Prepare state-level

12_compile_statelevel.ipynb:
- Input: Number of EVs (AFDC)
- Output: level_state.csv

### Compile highway data

13_highways_BG.py:
- Input: Primary roads shapefile
- For each BG, compute distance to nearest hwy
- Output: level_bg_'+state +'_hwy.csv 

13c_highways_stations.py:
- Input: stations data (00_alt_fuel_stations (Apr 3 2023)_wFIPS.csv) and primary and secondary roads shapefiles (tl_2022_us_primaryroads/tl_2022_us_primaryroads.shp and TIGER_secondaryroads_2022/tl_2022_'+fips+'_prisecroads.shp)
- Compute distance of each station to nearest primary and secondary road
- Output: level_stations_'+state+'_hwy.csv

## 2*: Compilation of datasets

### 20*: Station-level dataset

20_compile_stationlevel.ipynb:
- Input: Stations (00_alt_fuel_stations (Apr 3 2023)_wFIPS.csv)
- Add BG-level socioeconomics (level_BG.csv)
- Add neighboring income (level_BG_'+state+'_wnbincome.csv)
- Add POI by top category using distance matrices
- Add mobility data (patternsonly_uniqueID_20250401.csv)
- Add county-level data (level_county.csv)
- Add state-level data (level_state.csv)
- Add highway data (level_stations_'+state+'_hwy.csv)
- Add number of stations nearby using distance matrices
- Output: 20_level_stations_US_compiled_'+label+'.csv

Based on the station-level dataset, station types can be clustered. This is done by Data Analysis code.

20c_clustering_kmeans_allUS.ipynb (SP):
- Input: Station-level data (20_level_stations_US_compiled_250415.csv)
- Selects number of clusters
- Clusters stations to station typology
- Output: Stations with clusters assigned (cluster_centers_kmeans_nc7_'+plotsavedate+'.csv)

20d_add_clusters.ipynb:
- Input: Station-level data (20_level_stations_US_compiled_250415.csv) and station-level clusters (clustering/clustering_labels_saved_'+plotsavedate+'.csv)
- Merge stations with labels
- Output: 20d_level_stations_US_compiled_250415_wlabels.csv

### 21*: BG-level dataset

21_compile_BGlevel.ipynb:
- Input: BG-level socioeconomic data (level_BG.csv)
- Add neighboring income (level_BG_'+state+'_wnbincome.csv)
- Add county-level data (level_county.csv)
- Add state-level data (level_state.csv)
- Add highway data (level_bg_'+state +'_hwy.csv)
- Add number of stations within BG (00_alt_fuel_stations (Apr 3 2023)_wFIPS.csv)
- Add POI by top category (01_compiled_'+state+'.csv)
- Add IRA info (level_BG_'+state+'_IRA.csv and level_BG_'+state+'_nbIRA.csv)
- Output: BG-level dataset (21_level_BG_US_compiled_'+label+'.csv)

21c_bglevel_add_clustertypes.ipynb:
- Input: BG-level dataset (21_level_BG_US_compiled_'+label+'.csv) and station-level dataset (20d_level_stations_US_compiled_250415_wlabels.csv)
- Add number of stations by cluster to BG
- Output: 21c_level_BG_US_compiled_wlabels_'+label+'.csv

### 22*: CT-level datatset

22_compile_tractlevel.ipynb:
- Input: BG-level dataset (21c_level_BG_US_compiled_wlabels_250702.csv)
- Compute CT-level dataset, depending on type of data
- Output: 22_level_CT_US_compiled_wlabels_250702.csv

### 23*: Recalculate income quantiles

23_recalculate_incomequantiles.ipynb:
- Input: BGlevel/22_level_BG_US_imputed_250702.csv and CTlevel/22_level_CT_US_compiled_wlabels_250702.csv

## Requirements
This code was run with Python 3.13.0 and the requirements.txt file in this folder. 
- Recalculates income quantiles based on imputed income data

- Output: BGlevel/23_level_BG_US_imputedquantiles_20250722.zip and CTlevel/23_level_CT_US_imputedquantiles_20250722.zip
