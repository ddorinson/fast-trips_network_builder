__copyright__ = "Copyright 2015 Contributing Entities"
__license__   = """
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import os
import pandas as pd
from numpy import NaN
#from .Logger import FastTripsLogger

class GTFS_Utilities2(object):
    """
    Documentation forthcoming.
    """

    #: File with routes.
    #: TODO document format
    
    def __init__(self, gtfs_dir, start_time, end_time, service_id = 'WEEKDAY'):
        """
        Constructor from dictionary mapping attribute to value.
        """
        #: Trips_stop_times DataFrame
        self.dir = gtfs_dir
        self.start_time = start_time
        self.end_time = end_time
        self.service_id = service_id
        #self.trips = self._get_trips(start_time, end_time, service_id)
        #self.all_trips_df = pd.DataFrame.from_csv(self.dir + '/trips.txt', index_col=False)
        self.df_all_stops_by_trips = self._get_trips_stop_times()
        self.df_stops_by_window = self._get_stops_by_window()
        self.trip_list = self._get_trip_list()
        self.departure_times = self._get_departure_times()
        self.schedule_pattern_dict = self.get_schedule_pattern()
        self.schedule_pattern_df = self.get_schedule_pattern_df()   
        self.unique_stop_sequences_df = self.df_all_stops_by_trips.groupby(['shape_id', 'stop_sequence']).first()
    def  _get_trips_stop_times(self):
        """
        Creates a merged dataframe consisting of trips & stop_ids for the start time, end time and service_id (from GTFS Calender.txt).
        This can include partial itineraries as only stops within the start and end time are included.  
        """
        trips_df = pd.DataFrame.from_csv(self.dir + '/trips.txt', index_col=False)
        print trips_df
        # Get the trips for this service_id
        trips_df = trips_df.loc[(trips_df.service_id == self.service_id)]
        print self.service_id
        print trips_df
        stop_times_df = pd.DataFrame.from_csv(self.dir + '/stop_times.txt', index_col=False)
        stop_times_df = self._make_sequence_col(stop_times_df, ['trip_id', 'stop_sequence'], 'trip_id', 'stop_sequence')
        # Add columns for arrival/departure in decimal minutes and hours:
        #stop_times_df['arrival_time_mins'] = stop_times_df.apply(self._convert_to_decimal_minutes, axis=1, args=('arrival_time',))
        # Some schedules only have arrival/departure times for time points, not all stops:
        if stop_times_df['departure_time'].isnull().any():
            stop_times_df['departure_time'].fillna('00:00:00', inplace=True)
            stop_times_df['departure_time_mins'] = stop_times_df.apply(self._convert_to_decimal_minutes, axis=1,args=('departure_time',))
            stop_times_df['departure_time_mins'].replace(0, NaN, inplace = True)
            stop_times_df['departure_time_mins'].interpolate(inplace = True)
        else:
            stop_times_df['departure_time_mins'] = stop_times_df.apply(self._convert_to_decimal_minutes, axis=1,args=('departure_time',))
        stop_times_df['departure_time_hrs'] = stop_times_df['departure_time_mins']/60
        stop_times_df['departure_time_hrs'] = stop_times_df['departure_time_hrs'].astype(int)
        #print stop_times_df
        # Get all trips for this time window
        trips_tw_df = stop_times_df.loc[(stop_times_df.departure_time_mins >= self.start_time) & (stop_times_df.departure_time_mins < self.end_time)]
        
        # Only need the trip_id column
        trips_tw_df = pd.DataFrame(trips_tw_df.trip_id)
        #print len(trips_tw_df)
        trips_tw_df = trips_tw_df.drop_duplicates('trip_id')
        
        # Merge trips on trip_id, so we can have shape_id. Use inner so we get trips for time window and service_id
        trips_tw_df = trips_tw_df.merge(trips_df, 'inner', left_on = ["trip_id"], right_on = ["trip_id"])
        print trips_df
        print trips_tw_df
        # Get all the stops for the trips that operate in this window, even if some of the stops occur outside the window
        trips_stop_times_df = stop_times_df.merge(trips_tw_df, 'right', left_on = ["trip_id"], right_on = ["trip_id"])
        trips_stop_times_df = trips_stop_times_df.sort(['trip_id', 'stop_sequence'])
       
        return trips_stop_times_df
        

    def _get_trip_list(self):
        trips = self.df_all_stops_by_trips.trip_id.tolist()
        trips = list(set(trips))   
        return trips
    
    def _get_stops_by_window(self):
         stops_by_window_df = self.df_all_stops_by_trips.loc[(self.df_all_stops_by_trips.departure_time_mins >= self.start_time) & (self.df_all_stops_by_trips.departure_time_mins < self.end_time)]
         return stops_by_window_df
    
        
    def _get_departure_times(self):
        """
        Returns a dictionary where the key is shape_id and the value is a list of departure times at the first stop for the time window 
        specified in the constructor. 
        """
        
        first_departure = self.df_stops_by_window.sort('stop_sequence', ascending=True).groupby('trip_id', as_index=False).first()
        first_departure = first_departure.loc[(first_departure.stop_sequence == 1)]
        departure_times = {k: g["departure_time_mins"].tolist() for k,g in first_departure.groupby("shape_id")}
        
        return departure_times

    
       
    def get_departure_times_by_ids(self, list_of_shape_ids):
        """
        Using the list_of_shape_ids parameter, returns a list of combined departure times at the first stop for the time window 
        specified in the constructor. This can be used to get departure times for indivudal TDM routes that represents more than 
        one shape_id. 
        """
        
        departure_time_dict = dict((k, self.departure_times[k]) for k in (list_of_shape_ids))
        departure_times = []
        # We are getting the departure times for one or more shape_ids so put them all 
        # in one list:oh
        for departure_time in departure_time_dict.values():    
            departure_times.extend(departure_time)
        
        return departure_times
        
    def get_trips_per_hour(self):
        """
        Returns a dictionary where key is shape_id and value is the number of departures from the first stop. Does this only for
        the time window specified in the constructor.  
        """
        # get unique trips:
        first_departure = self.df_stops_by_window.sort('stop_sequence', ascending=True).groupby('trip_id', as_index=False).first()
        first_departure = first_departure.loc[(first_departure.stop_sequence == 1)]
        first_departure = first_departure.groupby(['shape_id', 'departure_time_hrs'])['departure_time_hrs'].count()
        first_departure_df = pd.DataFrame(first_departure)
        first_departure_df.reset_index(level=0, inplace=True)
        first_departure_df = first_departure_df.rename(columns = {'departure_time_hrs' : 'frequency'})
        first_departure_df.reset_index(level=0, inplace=True)
        t = pd.pivot_table(first_departure_df, values='frequency', index=['shape_id'], columns=['departure_time_hrs'])
        t = t.fillna(0)
        for col in t.columns:
            if not col == 'shape_id':
                t = t.rename(columns = {col : 'hour_' + str(col)})
        
        return t

    def get_tph_rep_trip_id(self):
       
         #trips_tw_df = trips_tw_df.merge(trips_df, 'inner', left_on = ["trip_id"], right_on = ["trip_id"])
        a = self.df_all_stops_by_trips.merge(self.get_schedule_pattern_df(), 'inner', left_on=['trip_id'], right_on=['orig_trip_id'])
        #get the first stop for every trip
        first_departure = a.sort('stop_sequence', ascending=True).groupby('trip_id', as_index=False).first()
        #this may not be necessary
        first_departure = first_departure.loc[(first_departure.stop_sequence == 1)]
        first_departure = first_departure.groupby(['rep_trip_id', 'departure_time_hrs'])['departure_time_hrs'].count()
        first_departure_df = pd.DataFrame(first_departure)
        first_departure_df.reset_index(level=0, inplace=True)
        first_departure_df = first_departure_df.rename(columns = {'departure_time_hrs' : 'frequency'})
        first_departure_df.reset_index(level=0, inplace=True)
        t = pd.pivot_table(first_departure_df, values='frequency', index=['rep_trip_id'], columns=['departure_time_hrs'])
        t = t.fillna(0)
        for col in t.columns:
            if not col == 'rep_trip_id':
                t = t.rename(columns = {col : 'hour_' + str(col)})
        
        return t
             
        
    def get_weighted_trips_per_hour(self):
        #get the rounded mean departure time for each trip:
        a = self.df_all_stops_by_trips.groupby(['trip_id', 'shape_id'])['departure_time_hrs'].mean()
        b = pd.DataFrame(a)
        b.reset_index(level=0, inplace=True)
        b.reset_index(level=0, inplace=True)
        b['departure_time_hrs'] = b['departure_time_hrs'].round().astype(int)
        first_departure = b.groupby(['shape_id', 'departure_time_hrs'])['departure_time_hrs'].count()
        first_departure_df = pd.DataFrame(first_departure)
        first_departure_df.reset_index(level=0, inplace=True)
        first_departure_df = first_departure_df.rename(columns = {'departure_time_hrs' : 'frequency'})
        first_departure_df.reset_index(level=0, inplace=True)
        t = pd.pivot_table(first_departure_df, values='frequency', index=['shape_id'], columns=['departure_time_hrs'])
        t = t.fillna(0)
        for col in t.columns:
            if not col == 'shape_id':
                t = t.rename(columns = {col : 'hour_' + str(col)})
        
        return t

    def get_weighted_tph_rep_trip_id(self):
        #get the rounded mean departure time for each trip:
        a = self.df_all_stops_by_trips.merge(self.get_schedule_pattern_df(), 'inner', left_on=['trip_id'], right_on=['orig_trip_id'])
        #print a.head()
        a = a.groupby(['trip_id', 'rep_trip_id'])['departure_time_hrs'].mean()
        b = pd.DataFrame(a)
        b.reset_index(level=0, inplace=True)
        b.reset_index(level=0, inplace=True)
        b['departure_time_hrs'] = b['departure_time_hrs'].round().astype(int)
        first_departure = b.groupby(['rep_trip_id', 'departure_time_hrs'])['departure_time_hrs'].count()
        first_departure_df = pd.DataFrame(first_departure)
        first_departure_df.reset_index(level=0, inplace=True)
        first_departure_df = first_departure_df.rename(columns = {'departure_time_hrs' : 'frequency'})
        first_departure_df.reset_index(level=0, inplace=True)
        t = pd.pivot_table(first_departure_df, values='frequency', index=['rep_trip_id'], columns=['departure_time_hrs'])
        t = t.fillna(0)
        for col in t.columns:
            if not col == 'rep_trip_id':
                t = t.rename(columns = {col : 'hour_' + str(col)})
        
        return t

    

    def _make_sequence_col(self, data_frame, sort_list, group_by_col, seq_col):

        """
        Sorts a pandas dataframe using sort_list, then creates a column of sequential integers (1,2,3, etc.) for
        groups, using the group_by_col. Then drops the existing sequence column and re-names the new sequence column.
        """
        #sort on tripId, sequence
        data_frame = data_frame.sort(sort_list, ascending=[1,1])
        #create a new field, set = to the position of each record in a group, grouped by tripId
        data_frame['temp'] = data_frame.groupby(group_by_col).cumcount() + 1
        #drop the old sequence column
        data_frame = data_frame.drop(seq_col, axis=1)
        #rename new column:
        data_frame = data_frame.rename(columns = {'temp':seq_col})

        return data_frame

    def _convert_to_decimal_minutes(self, row, field):
        '''Convert HH:MM:SS to seconds since midnight, for comparison purposes.'''
        H, M, S = row[field].split(':')
        seconds = float(((float(H) * 3600) + (float(M) * 60) + float(S))/60)
        
        return seconds

    def get_schedule_pattern(self):
        """
        Returns a nested diciontary where the first level key is route_id and values are respresentative trip_ids that have unique stop sequences.
        These are are used as keys for the second level where each value is a dictinary that includes a list of trips_id's that share this
        stop pattern and a list of ordered stops.
        {route_id : trip_id {trips_ids : [list of trip ids], stops : [list of stops]}}
        """

        # Create a dictionary where the key is a tuple of trip_id, route_id and the value is a list of stop sequences for the trip
        # Need to use all the stops for the trips within the time window, even if those stops fall outside the time winwdow because we 
        # are interested in unique stop sequences 
        stop_sequence_dict = {k: list(v) for k,v in self.df_all_stops_by_trips.groupby(['trip_id', 'route_id'])['stop_id']}
        
        # Empty dictionary to store unique stop sequences
        my_dict = {}
        for key, value in stop_sequence_dict.iteritems():
            trip_id = key[0]
            route_id = key[1]
            # Handle some branching later on
            found = False
            # If this is the first trip for this route, just add it
            if not route_id in my_dict.keys():
                my_dict[route_id] = {trip_id : {'stops': value, 'trip_ids' : [trip_id]}}
            # Otherwise check to see if this stop sequence has already been added for this route
            else: 
                for k, v in my_dict[route_id].iteritems():
                    if value == v['stops']:
                        # This stop sequence has already been added for this route, add the trip_id to the list of trip_ids that have this sequence in common.
                        my_dict[route_id][k]['trip_ids'].append(trip_id)
                        found = True
                        break
                if not found:
                    # Add the stop sequence and route, trip info
                    my_dict[route_id][trip_id] = {'stops': value, 'trip_ids' : [trip_id]}
            # Set back to False for next iteration
            found = False
        return my_dict
    
    def get_schedule_pattern_df(self):
        rows = []
        for route_id, trips in self.schedule_pattern_dict.iteritems():
            for trip_id, data in trips.iteritems():
                for trip in data['trip_ids']:
                    #print trip
                    rows.append({'route_id' : route_id, 'trip_id1' : trip_id, 'trip_id2': trip})  
        df2 = pd.DataFrame(rows)
        df = self.df_all_stops_by_trips.drop_duplicates(['trip_id'])
        df2 = df2.merge(df[['trip_id','shape_id']], how ='right', left_on = ["trip_id2"], right_on = ["trip_id"])
        df2 = df2.rename(columns = {'trip_id1' : 'rep_trip_id', 'trip_id' : 'orig_trip_id'})
        df2 = df2.drop('trip_id2', 1)
        #b = df2.groupby('trip_id1').shape_id.nunique()
        #c = df2.shape_id.nunique()
        return df2
           
#test = GTFS_Utilities2(r'R:\Stefan\PSR_Consolidated\gtfs_puget_sound_consolidated', 0, 1440, '727A1137')
#test = GTFS_Utilities2(r'W:\gis\projects\stefan\Geodatabase\Model\Transit2014\GTFS\Pierce\Google_Transit', 0, 1440, 'FEB14-WKD')
test = GTFS_Utilities2(r'D:\fast_trips\last_working_copy\fast_trips_repo_121415\fast-trips_network_builder\outputs', 0, 1440, 'PSRC')
#test = GTFS_Utilities2(r'T:\2016February\Craig\gtfs-2040-kcm-a41674b', 0, 1440, 'weekday')
#test = GTFS_Utilities2(r'W:\gis\projects\stefan\Geodatabase\Model\Transit2014\GTFS\Metro\google_transit', 0, 1440, 'WEEKDAY')
#test = GTFS_Utilities2(r'W:\gis\projects\stefan\Geodatabase\Model\Transit2014\GTFS\Kitsap\modified_gtfs', 0, 1440, 'mtwtf_PSNS')
#test = GTFS_Utilities2(r'W:\gis\projects\stefan\Geodatabase\Model\Transit2014\GTFS\Everett\ET', 0, 1440, 'WD')

#test = GTFS_Utilities2(r'W:\gis\projects\stefan\Geodatabase\Model\Transit2014\GTFS\SoundTransit\gtfs', 0, 1440, 'WD')
#test = GTFS_Utilities2(r'W:\gis\projects\stefan\Geodatabase\Model\Transit2014\GTFS\WSF', 0, 1440, 20160105)
#test = GTFS_Utilities2(r'W:\gis\projects\stefan\Geodatabase\Model\Transit2014\GTFS\CommunityTransit\GTFS', 0, 1440, '14SEP-Weekday')


                
                                                                                   
     



        