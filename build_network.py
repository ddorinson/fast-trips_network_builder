import sys
import os 
import inro.emme.matrix as ematrix
import inro.emme.database.matrix
import inro.emme.database.emmebank as _eb
import numpy as np
import pandas as pd
import itertools
from itertools import groupby
from itertools import chain

from collections import defaultdict
import collections
from config.input_configuration import *
from functions.general_functions import *
from gtfs_classes.FareRules import *
from gtfs_classes.Trips import *
from gtfs_classes.StopTimes import *
from gtfs_classes.StopTimesFT import *
from gtfs_classes.Shapes import *
from gtfs_classes.Stops import *
from gtfs_classes.StopsFT import *
from gtfs_classes.Routes import *
from gtfs_classes.Transfers import *
from gtfs_classes.TransfersFT import *
from gtfs_classes.GTFS_Utilities import *

# Fare Files
df_fares = pd.DataFrame.from_csv('inputs/fares/fare_id.csv', index_col=False)
df_stops_zones = pd.DataFrame.from_csv('inputs/fares/stop_zones.csv', index_col=False)

# Shape ID to model route crosswalk: 
df_shape_id_crosswalk = pd.DataFrame.from_csv('inputs/gtfs_shapeID_to_lineID.csv', index_col = False)

# Model routes to shape_id can be one to many; create a list of shape_ids for each model route
shapes = {k: list(v) for k,v in df_shape_id_crosswalk.groupby("model_shape_id")["gtfs_shape_id"]}

# Get unique rows using id (which is also model route shape_id) and name of feed 
#(also the directory where the gtfs data is stored)
unique_rows = df_shape_id_crosswalk.drop_duplicates(['model_shape_id', 'feed'])

# Populate a dictionary where key is model route shape_id, and value is a dictionary withe feed name and list
# of published gtfs shape_ids (shapes).  
shape_id_dict = {}
for row in unique_rows.iterrows():
    shape_id_dict[row[1].model_shape_id] = {'shape_ids' : shapes[row[1].model_shape_id], 'feed' : row[1].feed}

# Now get a list of tuples that include unique feed and service id's.
unique_rows = df_shape_id_crosswalk.drop_duplicates(['feed'])
subset = unique_rows[['feed', 'service_id']]
schedule_tuples = [tuple(x) for x in subset.values]


def main():
    # Creat outputs dir if one does not exist
    if not os.path.exists('outputs'):
        os.makedirs('outputs')

    network_dict = {}
    last_departure_dict = {}
    # Lists to hold stop_times and trips records
    stop_times_list = []
    stops = []
    stops_list = []
    trips_list = []
    shapes_list = []
    routes_list = []
    fare_rules = FareRules()

    # Generates a unique ID 
    id_generator = generate_unique_id(range(1,999999))
    
    # Load all the networks into the network_dict
    for tod in highway_assignment_tod.itervalues():
        
        
        with _eb.Emmebank(banks_path + tod + '/emmebank') as emmebank:
            current_scenario = emmebank.scenario(1002)
            network = current_scenario.get_network()
            network_dict[tod] = network

    for tod, my_dict in transit_network_tod.iteritems():
        # A dictionary to hold an instance of GTFS_Utilities for each feed
        gtfs_dict = {}
        
        # Populate gtfs_dict
        for feed in schedule_tuples:
            gtfs_utils = GTFS_Utilities('inputs/published_gtfs/' + feed[0], my_dict['start_time'], my_dict['end_time'], feed[1])
            gtfs_dict[feed[0]] = gtfs_utils
        
     
        # Get the am or md transit network: 
        transit_network = network_dict[my_dict['transit_bank']]
        transit_attributes_df = pd.DataFrame.from_csv('inputs/' + tod + '_line_attributes.csv', index_col=False)
        print transit_attributes_df

        transit_network.create_attribute('TRANSIT_LINE', 'shape_id')
        transit_network.create_attribute('TRANSIT_LINE', 'route_id')
        transit_network.create_attribute('TRANSIT_LINE', 'short_name')

        # Schedule each route and create data structure (list of dictionaries) for trips and stop_times. 
        for transit_line in transit_network.transit_lines():
            configure_transit_line_attributes(transit_line, transit_attributes_df)
            departure_times = []
            
            # Check if departure times for this route come from published GTFS shape_ids:
            if transit_line.shape_id in shape_id_dict.keys():
                feed = shape_id_dict[transit_line.shape_id]['feed']
                ids = shape_id_dict[transit_line.shape_id]['shape_ids']
                departure_times = gtfs_dict[feed].get_departure_times_by_ids(ids)
               
            ###### ROUTES ######
            routes_list.extend(get_route_record(transit_line))
            
            ###### SHAPES ######
            shapes_list.extend(get_transit_line_shape(transit_line))
      
            ###### FARES ######
            # Get a list of ordered stops for this route
            list_of_stops = get_emme_stop_sequence(transit_line)
            
            # Add to stops_list for writing out stops.txt later
            stops.extend(list_of_stops)

            # Get the zones
            zone_list = get_zones_from_stops(list_of_stops, df_stops_zones)
    
            # Remove duplicates in sequence. [1,2,2,1] becomes [1,2,1]
            zone_list = [x[0] for x in groupby(zone_list)]
       
            # Get zone combos. Note: mode 'f' for ferry gets special treatment for PSRC. See function def.
            zone_combos = get_zone_combos(zone_list, transit_line.mode.id)
    
            # Return instance of fare_rules with populated dataframe
            populate_fare_rule(zone_combos, fare_rules.data_frame, transit_line, df_fares)

            ###### Schedule ######
            schedule_route(my_dict['start_time'], my_dict['end_time'], transit_line, id_generator, stop_times_list, trips_list, network_dict, 
                           last_departure_dict, departure_times)

    ###### STOPS ######
    stops = list(set(stops))
    stops_list = popualate_stops(transit_network, stops)
   
            
    # Instantiate classes
    shapes = Shapes(shapes_list)
    stop_times = StopTimes(stop_times_list)
    stop_times_ft = StopTimesFT(stop_times_list)
    trips = Trips(trips_list)
    stops = Stops(stops_list)
    stops_ft = StopsFT(stops_list)
    routes = Routes(routes_list)

    #create transfers, depdendent on stops class:
    transfer_list = stop_to_stop_transfers(stops.data_frame, 2640)
    transfers = Transfers(transfer_list)
    transfers_ft = TransfersFT(transfer_list)

    
    # Drop duplicate records
    fare_rules.data_frame.drop_duplicates(inplace = True)
    routes.data_frame.drop_duplicates(inplace = True)
    routes.data_frame = routes.data_frame.groupby('route_id').first().reset_index()
    # Write out text files
    shapes.data_frame.to_csv('outputs/shapes.txt', index = False)
    stop_times.data_frame.to_csv('outputs/stop_times.txt', index = False)
    stop_times_ft.data_frame.to_csv('outputs/stop_times_ft.txt', index = False)
    stops.data_frame.to_csv('outputs/stops.txt', index = False)
    stops_ft.data_frame.to_csv('outputs/stops_ft.txt', index = False)
    trips.data_frame.to_csv('outputs/trips.txt', index = False)
    fare_rules.data_frame.to_csv('outputs/fare_rules.txt', index = False)
    routes.data_frame.to_csv('outputs/routes.txt', index = False)
    transfers.data_frame.to_csv('outputs/transfers.txt', index = False)
    transfers_ft.data_frame.to_csv('outputs/transfers_ft.txt', index = False)
if __name__ == "__main__":
    main()