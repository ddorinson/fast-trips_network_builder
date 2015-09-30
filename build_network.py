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
from gtfs_classes.Shapes import *
from gtfs_classes.Stops import *
from gtfs_classes.Routes import *

# Fare Files
df_fares = pd.DataFrame.from_csv('inputs/fares/fare_id.csv', index_col=False)
df_stops_zones = pd.DataFrame.from_csv('inputs/fares/stop_zones.csv', index_col=False)

# A place to store in-memory emme networks
network_dict = {}

def main():
    # Creat outputs dir if one does not exist
    if not os.path.exists('outputs'):
        os.makedirs('outputs')

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
            #transit_line.shape_id = int(transit_line.id) + my_dict['tod_int']
            #transit_line.route_id = int(transit_line["@rteid"])
            print transit_line.shape_id
            
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
            schedule_route(my_dict['start_time'], my_dict['end_time'], transit_line, id_generator, stop_times_list, trips_list, network_dict)

    ###### STOPS ######
    stops = list(set(stops))
    stops_list = popualate_stops(transit_network, stops)
   
            
    # Instantiate classes
    shapes = Shapes(shapes_list)
    stop_times = StopTimes(stop_times_list)
    trips = Trips(trips_list)
    stops = Stops(stops_list)
    routes = Routes(routes_list)
    
    # Drop duplicate records
    fare_rules.data_frame.drop_duplicates(inplace = True)
    routes.data_frame.drop_duplicates(inplace = True)
    routes.data_frame = routes.data_frame.groupby('route_id').first().reset_index()
    # Write out text files
    shapes.data_frame.to_csv('outputs/shapes.txt', index = False)
    stop_times.data_frame.to_csv('outputs/stop_times.txt', index = False)
    stops.data_frame.to_csv('outputs/stops.txt', index = False)
    trips.data_frame.to_csv('outputs/trips.txt', index = False)
    fare_rules.data_frame.to_csv('outputs/fare_rules.txt', index = False)
    routes.data_frame.to_csv('outputs/routes.txt', index = False)

if __name__ == "__main__":
    main()