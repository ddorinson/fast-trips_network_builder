import os
import pandas as pd

class Calendar(object):
    
    """
    Trips. 
    """
    columns = ['service_id','monday' ,'tuesday','wednesday','thursday','friday','saturday','sunday','start_date','end_date'] 
    def __init__(self, data):
        """
        Constructor to populate DataFrame from list of dictionaries where each dictionary holds 
        row data for GTFS Trips.txt. 
        """
        #: Trips_stop_times DataFrame
        
        self.data_frame = pd.DataFrame(data, columns = self.columns)