# fast-trips network builder 
This repository is to provide all the supply-side network input files for [fast-trips](http://fast-trips.mtc.ca.gov/). A [GTFS-PLUS transit network](https://developers.google.com/transit/gtfs/) consists of [transit assignment data files](https://github.com/psrc/soundcast/blob/5ce7547a8384df367c92d3e48c54eea86228f47e/scripts/summarize/standard/daily_bank.py) from [Soundcast](https://github.com/psrc/soundcast/wiki) that together describe a network of transit service. 


**version**: 0.0.1  
**updated**: 14 August 2017  
**created**: 09 september 2015  
**authors**:  

 * Stefan Coe  (Puget Sound Regional Council) 
 * Angela Yang (Puget Sound Regional Council) 

# Full Documentation
Transit Network Design Specification v0.2, [technical memo](http://fast-trips.mtc.ca.gov/library/T2-NetworkDesign-StaticCopy-Sept2015V0.2.pdf). 

# Related Project
[fast-trips](https://github.com/BayAreaMetro/fast-trips)

[Soundcast](https://github.com/psrc/soundcast)

[GTFS-PLUS](https://github.com/osplanning-data-standards/GTFS-PLUS)

[fast-trips Demand Converter](https://github.com/psrc/fast-trips_demand_converter)

# Setup
Following the steps below to run the network builder. 
 * Download and install [Anaconda python 2.7 package](https://www.anaconda.com/download/)
 * If you need run Soundcast to get transit assignment data files, follow the [Soundcast setup steps](https://github.com/psrc/soundcast/wiki/Soundcast-Install)
 
# Input
The inputs of network builder consist of: 
* [Soundcast transit bank](https://github.com/psrc/soundcast/blob/5ce7547a8384df367c92d3e48c54eea86228f47e/scripts/summarize/standard/daily_bank.py) for transit assignment. It could be generate from Soundcast model run. Please make sure you have hourly transit banks. 

* A network builder MUST include the following input files:

Filename 			| Description										
----------			| -------------										
[`fare_id.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/fares/fare_id.csv)	| fare id									
[`stop_zones.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/fares/stop_zones.csv)		| stop zones		
[`fare_rules_ft.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/fares/fare_rules_ft.csv)| fair rules					
[`fare_attributes.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/fares/fare_attributes.csv)				| fare attributes								
[`fare_attributes_ft.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/fares/fare_attributes_ft.csv)		| fare attributes for fast trips		
[`fare_transfer_rules.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/fares/fare_transfer_rules.csvd)			| fare transfer rules									
[`vehicles.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/vehicles.csv)		| type of vehicles				
[`timed_transfers.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/timed_transfers.csv)				| transfer time								
[`line_attribtes.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/line_attributes.csv)		| Get TAZ Nodes for walk access				
[`gtfs_shapeID_to_lineID.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/gtfs_shapeID_to_lineID.csv)	| Shape ID to model route crosswalk  		
[`sc_headways.csv`](https://github.com/psrc/fast-trips_network_builder/blob/master/inputs/sc_headways.csv)	| optional, generate gtfs_shapeID_to_lineID.csv									
`hourly_trips33.txt`			| optional, generate gtfs_shapeID_to_lineID.csv									


# Output
* Output is specified by [GTFS-PLUS transit network](https://github.com/osplanning-data-standards/GTFS-PLUS) for network of transit service. The data files including schedules, access, egress and transfer information.

NOTE: [GTFS-Plus Data Standards Repository](https://github.com/osplanning-data-standards/GTFS-PLUS) is a draft specification and still under development.

# Getting Started
Run the [configure file](https://github.com/psrc/fast-trips_network_builder/blob/master/config/input_configuration.py) under python 2.7 environment. 

NOTE: Please keep transit network time of day bank setting consistent with [transit demand](https://github.com/psrc/fast-trips_demand_converter). By doing this, we won't have any transit time conflict in the fast-trips model run. 

# License
This project is licensed under [Apache 2.0](https://github.com/psrc/fast-trips_network_builder/blob/Angela/LICENSE.md)



