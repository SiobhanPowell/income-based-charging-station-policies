# Analysis

This repository accompanies the manuscript "Income-Based Policies for Public Electric Vehicle Charging Station Deployment" by Siobhan Powell (ETH Zürich) and Marie-Louise Arlt (University of Bayreuth and Bavarian Center of Battery Technology).

### Organization

This folder contains the analysis run for the paper: 
1. Regression presented in Table 1.
2. Clustering of station locations, including some associated figures like the elbow plot.
3. Repeating the regression from Table 1 separately for each cluster or for each state.
4. Alternatives/extensions to the main Table 1 regression, presented in the Supplementary Information.
5. Alternative regressions using the Bipartisan Infrastructure Law label of disadvantaged communities, presented in the Supplementary Information.

The file ``clustering_allUS_preprocessing.py`` is used to preprocess all data for clustering, so that comparisons across different clustering methods use consistent inputs. 

### Data

Outputs of files 2 and 3 are published in our data repository and later used in the ``Plotting`` folder to produce some of the figures. Unfortunately the raw input data cannot be published due to privacy concerns. 

### Requirements

This code was run with Python version 3.10.7 and the packages listed in ``requirements_short.txt``.