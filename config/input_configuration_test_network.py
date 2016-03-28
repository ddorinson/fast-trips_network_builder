import collections
# This file contains input parameters imported by Fast-Trips Network Building scripts.   

# Default dwell time in decimal minutes
DWELL_TIME = 0

#Service ID Field 
SERVICE_ID = 'tntransit'
use_published_departure_times = True
# Location of assingment banks
banks_path = 'D:/Stefan/fast_trips_working/test/Banks/'

agency_list = [{'agency_id' : 'tntransit', 'agency_name' : 'tntransit', 'agency_url' : "http://www.sfcta.org", 'agency_timezone' : 'US/Pacific'}]
calender_list = [{'service_id' : 'tntransit', 'monday' : 1 ,'tuesday' : 1,'wednesday' : 1, 'thursday' : 1,'friday' : 1,'saturday' : 1, 'sunday' : 1, 
            'start_date' : '20150101', 'end_date' : '20151231'}]

##### Network Dictionaries:
# We currently have two disctinct transit networks- AM and MD - and we use them for multiple assignment periods. 
# 'transit_bank'- The transit network to use for a given time period (AM or MD). We use the same am transit network for 6to7, 7to8, and 8to9 assignments, 
#                 so we only need to use one. Same for MD (9to10, 10to14, 14to15). This will change for 2014 when we will have one network with headways 
#                 for each time period, like SFCTA currently does. 

# 'start_time'-   The mininum time a route can leave its first stop. Our transit demand starts at 6:00 and ends at 15:00, but we can not 
#                 have a hard start of the schedule at 6 because we would be missing service from routes that begin before 6:00 and 
#                 have stops that occur after 6:00. For now, lets start the schedule building at 5 using am peak service levels.

# "end_time'-     The max time a route can leave it's first stop. Note that all stops will be completed even if they occur after end_time. 

transit_network_tod = collections.OrderedDict()
transit_network_tod['am'] = {'transit_bank' : '7to8', 'start_time' : 900, 'end_time' : 1080, 'tod_int' : 10000}
#transit_network_tod['md'] = {'transit_bank' :'9to10', 'start_time' : 540, 'end_time' : 900, 'tod_int': 20000 }


# The highway asssignment bank that is used to get link speed/time. 
highway_assignment_tod = {5: '7to8', 6: '7to8', 7: '7to8', 8: '7to8', 9: '7to8', 10: '7to8', 11 : '7to8',
                          12: '7to8', 13 : '7to8', 14 : '7to8', 15 : '7to8', 16 : '7to8', 17:'7to8', 18:'7to8', 19:'7to8'}

# Sometimes we need to get travel times from road networks that are not part of our static transit network time periods (6-9, 9-15). It's possible that a link
# belonging to a given transit route does not exist in these networks so we must have a fall back network. For example, a route departs it's first stop at 8:55 
# and continues make stops past 9. Any such stop should get it's stop to stop travel time from the 9to10 auto assignment bank, but it's possible that the link does 
# not exist (e.g. bus only lane that reverts back to GP during non-peak) for this network. In these cases, get the travel time from the '8to9' highway assignment bank.
# key = auto_assignment bank that does not contain the link, value = auto_assignment  bank that should be used instead. 
fall_back_dict = {'5to6' : '6to7', '9to10' : '8to9', '10to14' : '8to9', '15to16' : '14to15'}

route_type_dict = {'r' : 2, 'c' : 2, 'b' : 3, 'p' : 3, 'f' : 4}