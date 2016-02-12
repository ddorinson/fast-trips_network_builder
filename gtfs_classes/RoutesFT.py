import os
import pandas as pd

class RoutesFT(object):
    
    """
    Routes. 
    """
    columns = ['route_id', 'mode', 'proof_of_payment'] 
    def __init__(self, data):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS routes.txt. 
        """
        #: Trips_stop_times DataFrame
        
        self.data_frame = pd.DataFrame(data, columns = self.columns)
    
