# Plotting

This repository accompanies the manuscript "Income-Based Policies for Public Electric Vehicle Charging Station Deployment" by Siobhan Powell (ETH Zürich) and Marie-Louise Arlt (University of Bayreuth and Bavarian Center of Battery Technology).

### Organization

This folder contains the notebooks used to generate the figures in the main paper and the supplementary information. 

Here we describe the files for the main paper figures:
1. ``figure1ab_figureS1_maps.ipynb``: Figures 1a, 1b, and S1. Maps of income and charging station counts by county.
2. ``figure1c_map.ipynb``: Figure 1c. Map of EV adoption by state.
3. ``figure1de_figureS2_square.ipynb``: Figures 1d, 1e, and S2. Distribution of stations by income.
4. ``figure2.ipynb``: Figure 2a, 2b, and 2c. Maps of LA county and count of stations and POIs by relative income.
5. ``figure3b_pie.ipynb``: Figure 3b. Pie chart of cluster sizes.
6. ``figure3c_access.ipynb``: Figure 3c. Breakdown of access by station cluster in terms of pricing, ownership, plug type, and charging network. 
7. ``figure4abc_bar.ipynb``: Figure 4a, 4b, and 4c. Distribution of station types by income.
8. ``figure4d_regression.ipynb``: Figure 4d. Regression coefficients by cluster.
9. ``figure5a_maps.ipynb``: Figure 5a. Map of cluster distribution by state.
10. ``figure5b_scatter.ipynb``: Figure 5b. Relationship between cluster share and EV stock in each state.
11. ``figure6a_map.ipynb``: Figure 6a. Map of neighborhood effect coefficients by state.
12. ``figure6b_scatter.ipynb``: Figure 6b. Relationship between regression coefficients and EV stock by state. 

The files ``figureS*.ipynb`` are used to generate the SI figures. 

### Data

Each figure from the main paper can be reproduced by loading the data saved in the data repository. For some, the whole notebook can be run using this data. For others, the relevant data is first *produced* in the notebook and then used for the figure. In those cases, the notebook should be run from the midpoint after the saved data is reloaded. Data used in the SI figures can be made available upon request. Unfortunately the raw input data cannot be published due to privacy concerns. 

### Requirements

This code was run with Python version 3.10.7 and the packages listed in ``requirements_short.txt`` in the Analysis folder.