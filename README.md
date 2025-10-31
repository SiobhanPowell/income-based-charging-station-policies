# Income-Based Policies for Public Electric Vehicle Charging Station Deployment

This repository accompanies the manuscript "Income-Based Policies for Public Electric Vehicle Charging Station Deployment" by Siobhan Powell (ETH Zürich) and Marie-Louise Arlt (University of Bayreuth and Bavarian Center of Battery Technology).

Contact:
- spowell (at) ethz (dot) ch
- arlt (at) uni-bayreuth (dot) de

Please cite this code as: Siobhan Powell and Marie-Louise Arlt. (2025). SiobhanPowell/income-based-charging-station-policies: (v1.0.1). Zenodo. doi: 10.5281/zenodo.17494751.

[![DOI](https://zenodo.org/badge/1087188066.svg)](https://doi.org/10.5281/zenodo.17494751). 

# Abstract

Widespread electric vehicle use is a key step to tackling transportation emissions, but adoption has yet to take-off beyond high-income communities. A lack of access to public charging stations can be a major barrier to adoption. In this paper, we analyze the distribution and typology of public charging stations found in low-, mid-, and high-income communities across the US. Our results identify a robust neighborhood advantage, where high income in the surrounding area coincides with higher numbers of public stations in lower income block groups. We further show that station types in lower income areas are associated with shorter stops, suggesting they are designed to serve pass-through demand. Future income-based policies for public charging infrastructure should consider how new stations fit local residents' mobility patterns and should use both local and neighborhood and income, to better target their support toward equal access for all future electric vehicle drivers.

# Structure of the Repository

**Data_PreProcessing**: Creates the BG-level and station-level datasets used for the analysis. Please see the ReadMe in the folder Data_PreProcessing for further details.

**Analysis**: Uses the station-level dataset to derive the topology of stations (clustering) and leverages the BG-level dataset for the analysis of the neighborhood effect.

**Plotting**: Plots figures based on results of folder "Analysis".

To run the code, please initialize a virtual environment and install the packages listed in each folder's requirement.txt .

# Data

Please consult the manuscript on the original data. All data is public except for mobility data which was provided confidentially by SafeGraph. The data files needed to reproduce the figures in the main manuscript are published here: [submitted to Mendeley Data, pending moderator review].

# Acknowledgements

The authors thank SafeGraph for providing the mobility data. S. Powell gratefully acknowledges support from an ETH Postdoctoral Fellowship and an Ambizione Grant from the Swiss National Science Foundation. Marie-Louise Arlt gratefully acknowledges funding received from the European Union’s Framework Programme for Research and Innovation Horizon 2020 (2014-2020) under the Marie Sklodowska-Curie Grant Arrangement No. 754388 (LMUResearchFellows) and from LMUexcellent, funded by the Federal Ministry of Education and Research (BMBF) and the Free State of Bavaria under the Excellence Strategy of the German Federal Government and the Länder.
