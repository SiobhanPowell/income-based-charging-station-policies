"""This file is used to clean, normalize, and transform the data for clustering. This is done in a dedicated class so that multiple analyses comparing different clustering methods are sure to do it exactly the same way. """


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import PowerTransformer
import sklearn 
import json
import copy


class ClusteringData(object):
    
    def __init__(self, df=None, savedate='20250414'):
        
        if df is not None:
            self.df = df
        self.savedate = savedate
# note: commute time is above, e.g. commute40 is 40-44 minutes, commute45 is 45-59, commute 60 is 60-89, commute 0 is 0-4

        self.cols_cluster = ['PopDensity_inBG', 'ResCars_pp_BG', 
                             'median_number_rooms_byBG', 'housingunits_percapita_byBG',
                             'share_white_byBG', 'share_nonwhite_byBG', 
                             'share_mode_public_byBG', 'share_mode_walkbike_byBG', 'share_mode_car_byBG', 
                             'short_commute_0to25min_byBG', 'medium_commute_25to45min_byBG', 'long_commute_45+min_byBG', 
                             'share_housing_owners_byBG', 'share_housing_detached_byBG', 'share_somehighereducation_byBG', 
                             'nostations_nearby_500', 'no_PoI_500',
                             'share_Restaurants_and_Bars_500', 'share_Commercial_500', 'share_Office_500',
                             'share_Education/Child_Care_500', 'share_Medical_500', 'share_Recreation_500',
                             'share_Gas_Station_500', 'share_Manufacturing_500', 'share_Transit_500', 'share_Hotels_500',
                             'nearest_highway_km', 'nearest_primarysecondary_km', 'distance_from_home',
                             'pop_by_day_Monday', 'pop_by_day_Tuesday', 'pop_by_day_Wednesday', 'pop_by_day_Thursday',
                             'pop_by_day_Friday', 'pop_by_day_Saturday', 'pop_by_day_Sunday',
                             'dwell_time_bucket_<5', 'dwell_time_bucket_5-10', 'dwell_time_bucket_11-20',
                             'dwell_time_bucket_21-60', 'dwell_time_bucket_61-120', 'dwell_time_bucket_121-240',
                             'dwell_time_bucket_>240',
                             'popularity_by_hour_0to3', 'popularity_by_hour_3to6', 'popularity_by_hour_6to9',
                             'popularity_by_hour_9to12', 'popularity_by_hour_12to15', 'popularity_by_hour_15to18',
                             'popularity_by_hour_18to21', 'popularity_by_hour_21to24']

        self.col_renaming = {'ResCars_pp_BG':'Cars pp',
                             'share_housing_detached_byBG':'Detached houses',
                             'share_housing_owners_byBG':'Home owners',
                             'nearest_highway_km':'Dist to highway', 
                             'median_number_rooms_byBG':'Num rooms',
                             'housingunits_percapita_byBG':'Units pp',
                             'share_white_byBG':'White',
                             'share_somehighereducation_byBG':'Higher Ed',
                             'share_mode_car_byBG':'Car commute',
                             'PopDensity_inBG':'Pop density',
                             'nostations_nearby_500':'Stations 500m',
                             'share_Transit_500':'Transit 500m',
                             'share_mode_public_byBG':'Public commute',
                             'share_nonwhite_byBG':'Non-white',
                             'nostations_nearby_1000':'Stations 1km',
                             'no_PoI_500':'POIs 500m',
                             'share_mode_walkbike_byBG':'Active commute',
                             'nostations_nearby_100':'Stations 100m',
                             'popularity_by_hour_12to15':'12pm-3pm',
                             'median_dwell':'Med dwelltime',
                             'popularity_by_hour_6to9':'6am-9am',
                             'dwell_time_bucket_>240':'Dwell 4h+',
                             'dwell_time_bucket_121-240':'Dwell 2-4h',
                             'popularity_by_hour_9to12':'9am-12pm',
                             'share_Recreation_500':'Recreation 500m',
                             'popularity_by_hour_15to18':'3pm-6pm',
                             'dwell_time_bucket_61-120':'Dwell 1-2h',
                             'share_Medical_500':'Medical 500m',
                             'pop_by_day_Thursday':'Thursdays',
                             'pop_by_day_Wednesday':'Wednesdays',
                             'pop_by_day_Tuesday':'Tuesdays',
                             'share_Education/Child_Care_500':'School/daycare 500m',
                             'short_commute_0to25min_byBG':'Short commute',
                             'pop_by_day_Monday':'Mondays',
                             'share_Manufacturing_500':'Manufacturing 500m',
                             'share_Office_500':'Offices 500m',
                             'share_Restaurants_and_Bars_500':'Rest/Bars 500m',
                             'popularity_by_hour_18to21':'6pm-9pm',
                             'pop_by_day_Saturday':'Saturdays',
                             'pop_by_day_Sunday':'Sundays',
                             'dwell_time_bucket_21-60':'Dwell 20-60min',
                             'medium_commute_25to45min_byBG':'Medium commutes',
                             'long_commute_45+min_byBG':'Long commutes',
                             'av_income_10km':'Avg income 10km',
                             'av_income_50km':'Avg income 50km',
                             'median_household_income_byBG':'HH income',
                             'nearest_primarysecondary_km':'Dist major rd',
                             'share_Gas_Station_500':'Gas 500m',
                             'dwell_time_bucket_5-10':'Dwell 5-10min',
                             'dwell_time_bucket_<5':'Dwell <5min',
                             'pop_by_day_Friday':'Fridays',
                             'share_Commercial_500':'Commercial 500m',
                             'dwell_time_bucket_11-20':'Dwell 11-20min',
                             'popularity_by_hour_0to3':'12am-3am',
                             'popularity_by_hour_3to6':'3am-6am',
                             'distance_from_home':'Dist from home',
                             'share_Hotels_500':'Hotels 500m',
                             'popularity_by_hour_21to24':'9pm-12am'}
        
        self.column_ordering = pd.DataFrame({'Column':self.cols_cluster})
        self.column_reordering_dict = {'popularity_by_hour_0to3':0,
                                       'popularity_by_hour_3to6':0,
                                       'popularity_by_hour_6to9':0,
                                       'popularity_by_hour_9to12':0, 
                                       'popularity_by_hour_12to15':0,
                                       'popularity_by_hour_15to18':0,
                                       'popularity_by_hour_18to21':0,
                                       'popularity_by_hour_21to24':0, 
                                       'pop_by_day_Monday':1,
                                       'pop_by_day_Tuesday':1, 
                                       'pop_by_day_Wednesday':1,
                                       'pop_by_day_Thursday':1, 
                                       'pop_by_day_Friday':1, 
                                       'pop_by_day_Saturday':1, 
                                       'pop_by_day_Sunday':1,
                                       'dwell_time_bucket_<5':2, 
                                       'dwell_time_bucket_5-10':2,
                                       'dwell_time_bucket_11-20':2, 
                                       'dwell_time_bucket_21-60':2, 
                                       'dwell_time_bucket_61-120':2,
                                       'dwell_time_bucket_121-240':2,
                                       'dwell_time_bucket_>240':2, 
                                       'no_PoI_500':3,
                                       'share_Gas_Station_500':3,
                                       'share_Restaurants_and_Bars_500':3,
                                       'share_Recreation_500':3,
                                       'share_Commercial_500':3, 
                                       'share_Manufacturing_500':3, 
                                       'share_Office_500':3, 
                                       'share_Medical_500':3,
                                       'share_Education/Child_Care_500':3,
                                       'share_Hotels_500':3, 
                                       'share_Transit_500':3, 
                                       'distance_from_home':4,
                                       'nearest_highway_km':4, 
                                       'nearest_primarysecondary_km':4, 
                                       'nostations_nearby_500':4, 
                                       'short_commute_0to25min_byBG':4,
                                       'medium_commute_25to45min_byBG':4,
                                       'long_commute_45+min_byBG':4, 
                                       'ResCars_pp_BG':4,
                                       'share_mode_car_byBG':4,
                                       'share_mode_public_byBG':4, 
                                       'share_mode_walkbike_byBG':4,
                                       'PopDensity_inBG':5,
                                       'housingunits_percapita_byBG':5, 
                                       'share_housing_detached_byBG':5,
                                       'share_housing_owners_byBG':5, 
                                       'median_number_rooms_byBG':5, 
                                       'share_white_byBG':5, 
                                       'share_nonwhite_byBG':5,
                                       'share_somehighereducation_byBG':5}

        for key, val in self.column_reordering_dict.items():
            ind = self.column_ordering[self.column_ordering['Column']==key].index
            self.column_ordering.loc[ind, 'Col_Cluster_forDisplay_v2'] = val
    
        for i, key in enumerate(list(self.column_reordering_dict.keys())):
            ind = self.column_ordering[self.column_ordering['Column']==key].index
            self.column_ordering.loc[ind, 'Display_Order_2'] = i

        self.column_labels = {0:'Evening/Overnight',
                         1:'Suburban',
                         2:'Weekday Daytime',
                         3:'Weekend shopping',
                         4:'Dense cities',
                         5:'Remote',
                         6:'Short stops',
                         7:'Commuters'}
        self.section_labels = {0:'Time of the Day', 1:'Day of the Week', 2:'Dwell Time', 3:'Nearby POIs', 4:'Travel-Related Descriptors', 5:'Other'}
        
        for i in self.column_ordering.index:
            self.column_ordering.loc[i, 'Columns_NiceName'] = self.col_renaming[self.column_ordering.loc[i, 'Column']]
    
    def clean(self):
        
        census_cols = ['median_number_rooms_byBG', 'share_white_byBG', 'share_mode_public_byBG', 'share_mode_car_byBG',
                       'housingunits_percapita_byBG', 'share_housing_owners_byBG', 'share_housing_detached_byBG', 
                       'PopDensity_inBG', 'ResCars_pp_BG', 'share_nonwhite_byBG', 'share_mode_walkbike_byBG', 
                       'short_commute_0to25min_byBG', 'medium_commute_25to45min_byBG', 'long_commute_45+min_byBG', 
                       'share_somehighereducation_byBG', 'total_pop_byBG']
        zero_cols = ['share_Commercial_500', 'share_Education/Child_Care_500', 'share_Gas_Station_500', 'share_Hotels_500',
                     'share_Manufacturing_500', 'share_Medical_500', 'share_Office_500', 'share_Recreation_500', 
                     'share_Restaurants_and_Bars_500', 'share_Transit_500']
        pattern_cols = ['raw_visit_counts', 'distance_from_home', 'pop_by_day_Monday', 'pop_by_day_Tuesday',
                        'pop_by_day_Wednesday', 'pop_by_day_Thursday', 'pop_by_day_Friday', 'pop_by_day_Saturday',
                        'pop_by_day_Sunday', 'dwell_time_bucket_<5', 'dwell_time_bucket_5-10', 'dwell_time_bucket_11-20',
                        'dwell_time_bucket_21-60', 'dwell_time_bucket_61-120', 'dwell_time_bucket_121-240',
                        'dwell_time_bucket_>240', 'popularity_by_hour_0to3', 'popularity_by_hour_3to6',
                        'popularity_by_hour_6to9', 'popularity_by_hour_9to12', 'popularity_by_hour_12to15',
                        'popularity_by_hour_15to18', 'popularity_by_hour_18to21', 'popularity_by_hour_21to24',
                        'raw_visit_counts']
        unitlist = ['BGFP', 'TRACTFP', 'STATEFP', 'COUNTYFP']
        
        for col in zero_cols:
            inds = self.df[self.df[col].isna()].index
            self.df.loc[inds, col] = 0

        for col in census_cols:
            inds = self.df[self.df[col].isna()].index
            nonan = self.df[~self.df[col].isna()]
            meanvals = {col2 : dict(nonan.groupby(col2)[col].mean()) for col2 in unitlist}
            for i in inds:
                if self.df.loc[i, 'BGFP'] in meanvals['BGFP'].keys():
                    self.df.loc[i, col] = meanvals['BGFP'][self.df.loc[i, 'BGFP']]
                elif self.df.loc[i, 'TRACTFP'] in meanvals['TRACTFP'].keys():
                    self.df.loc[i, col] = meanvals['TRACTFP'][self.df.loc[i, 'TRACTFP']]
                elif self.df.loc[i, 'COUNTYFP'] in meanvals['COUNTYFP'].keys():
                    self.df.loc[i, col] = meanvals['COUNTYFP'][self.df.loc[i, 'COUNTYFP']]
                elif self.df.loc[i, 'STATEFP'] in meanvals['STATEFP'].keys(): 
                    self.df.loc[i, col] = meanvals['STATEFP'][self.df.loc[i, 'STATEFP']]
                else:
                    self.df.loc[i, col] = self.df[~self.df[col].isna()].mean()
                    
        for col in pattern_cols:
            inds = self.df[self.df[col].isna()].index
            nonan = self.df[~self.df[col].isna()]
            self.df.loc[inds, col] = nonan.loc[:, col].mean()
        
    def normalize(self):
        
        self.df.loc[self.df.loc[self.df['share_somehighereducation_byBG'] == np.inf].index, 'share_somehighereducation_byBG'] = 0
        self.df.loc[self.df.loc[self.df['housingunits_percapita_byBG'] == np.inf].index, 'housingunits_percapita_byBG'] = 0
        
        for col in ['pop_by_day_Monday', 'pop_by_day_Tuesday', 'pop_by_day_Wednesday', 'pop_by_day_Thursday', 
                    'pop_by_day_Friday', 'pop_by_day_Saturday', 'pop_by_day_Sunday',
                    'popularity_by_hour_0to3', 'popularity_by_hour_3to6', 'popularity_by_hour_6to9',
                    'popularity_by_hour_9to12', 'popularity_by_hour_12to15', 'popularity_by_hour_15to18',
                    'popularity_by_hour_18to21', 'popularity_by_hour_21to24','dwell_time_bucket_<5',
                    'dwell_time_bucket_5-10', 'dwell_time_bucket_11-20', 'dwell_time_bucket_21-60',
                    'dwell_time_bucket_61-120', 'dwell_time_bucket_121-240', 'dwell_time_bucket_>240']:
            inds_nonzero = self.df[self.df['raw_visit_counts'] > 0].index
            inds_zero = self.df[self.df['raw_visit_counts'] == 0].index
            self.df.loc[inds_nonzero, col] = self.df.loc[inds_nonzero, col] / self.df.loc[inds_nonzero, 'raw_visit_counts']
            self.df.loc[inds_zero, col] = 0
            
        inds_nonzero = self.df[self.df['total_pop_byBG'] > 0].index
        inds_zero_nan = self.df.loc[(self.df['total_pop_byBG'] == 0)&(self.df['ResCars_pp_BG'].isna())].index
        inds_zero_nonan = self.df.loc[(self.df['total_pop_byBG'] == 0)&(~self.df['ResCars_pp_BG'].isna())].index
        self.df.loc[inds_nonzero, 'ResCars_pp_BG'] = self.df.loc[inds_nonzero, 'ResCars_pp_BG'] / self.df.loc[inds_nonzero, 'total_pop_byBG']
        self.df.loc[inds_zero_nonan, 'ResCars_pp_BG'] = self.df.loc[inds_zero_nonan, 'ResCars_pp_BG'] / 1000 # what to do here? 
        self.df.loc[inds_zero_nan, 'ResCars_pp_BG'] = 0
        
    def transform(self, save=False):
        scaler = PowerTransformer(method='yeo-johnson')
        self.X_std = scaler.fit_transform(self.df.loc[:, self.cols_cluster]) 
        self.X_std_df = pd.DataFrame(self.X_std, columns=self.cols_cluster)
        
        if save:
            plt.figure()
            self.X2_copy.loc[:, self.cols_cluster].hist(figsize=(16, 20), layout=(11, 6))
            plt.tight_layout()
            plt.savefig('Figures/clustering_data_prefilter_'+self.savedate+'.pdf', bbox_inches='tight', dpi=400)
            plt.savefig('Figures/clustering_data_prefilter_'+self.savedate+'.png', bbox_inches='tight', dpi=400)
            plt.close()
            plt.figure()
            self.X_std_df.hist(figsize=(16, 20), layout=(11, 6))
            plt.tight_layout()
            plt.savefig('Figures/clustering_data_postfilter_'+self.savedate+'.pdf', bbox_inches='tight', dpi=400)
            plt.savefig('Figures/clustering_data_postfilter_'+self.savedate+'.png', bbox_inches='tight', dpi=400)
            plt.close()
            
        self.X_std_save = self.X_std_df.copy(deep=True)
        self.X_std_save['unique_ID'] = self.df.index

