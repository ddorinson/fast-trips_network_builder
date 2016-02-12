import os
import pandas as pd

class TripsFT(object):
    
    """
    Trips. 
    """
    columns = ['trip_id', 'vehicle_name'] 
    def __init__(self, data):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS Trips.txt. 
        """
        #: Trips_stop_times DataFrame
        
        self.data_frame = pd.DataFrame(data, columns = self.columns)