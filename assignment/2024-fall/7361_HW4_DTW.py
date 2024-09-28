# TASK 1. Calculate DTW values and interpret the results
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import pandas as pd
import itertools
from shapely.geometry import LineString
import geopandas as gpd
from shapely import wkt
import math

"""
# example 1
x = np.array([[1,1], [2,2], [3,3], [4,4], [5,5]])
y = np.array([[2,2], [3,3], [4,4]])
distance, path = fastdtw(x, y, dist=euclidean) # euclidean means that when matching each pair of points in dtw, you are applying euclidean distance
print(distance)
# 2.8284271247461903

# example 2
x = np.array([[1,1], [2,2], [3,3], [4,4], [4,4], [4,4], [5,5]])
y = np.array([[2,2], [3,3], [4,4]])
distance, path = fastdtw(x, y, dist=euclidean) # euclidean means that when matching each pair of points in dtw, you are applying euclidean distance
print(distance)
# 2.8284271247461903
"""

# read data and store user id and location into a dict.
counter_user = 0
user_coor_dict = {}  # a dictionary that stores the coordinates of all users. Key: user ID, value: a list that stores the coordinates of this user

with open('weibo_users_subset.txt') as f:
    file = f.readline() # skip header
    
    # calculate the rog of all users in the provided file
    file = f.readlines()  # read all the lines in the weibo file
    previous_user_id = -1 # track if current user is the first user
    
    for j in file:
        data =j.strip('\n').split('\t')
        current_user_id = data[0] # get user id of the current row
        current_user_lon = float(data[1]) # get longitude of the current row
        current_user_lat= float(data[2]) # get latitude of the current row
        
        if current_user_id in user_coor_dict: # if some of this user's lat/lon have been added to the dictionary
            user_coor_dict[current_user_id].append((current_user_lon,current_user_lat)) # keep adding to the lon/lat list where the key is the user id
        
        else: # if this is a new user
            # create a new key
            user_coor_dict[current_user_id]= []

            # add current lat/lon as the first point of this user
            user_coor_dict[current_user_id].append((current_user_lon, current_user_lat))
            counter_user += 1
            print('user ' + str(counter_user) + ' extracted')
        previous_user_id = current_user_id

print (user_coor_dict) # done reading data


#calculate the dtw distance between users
out_file = open("weibo_subset_dtw_dist.txt", 'w') # open output file to store the calculated dtw distances
out_file.write("id1\tid2\tdtw_dist\n")

"""
# test
arr = {'1182255057': [(12938246.08, 4852272.833),
  (12949011.78, 4859345.615),
  (12949205.48, 4865799.87),
  (12949866.16, 4865356.959),
  (12953958.93, 4853185.663)],
 '1187065643': [(12954884.78, 4850831.921),
  (12962122.44, 4854572.049),
  (12949633.5, 4833106.924),
  (12949546.9, 4827651.198),
  (12954612.05, 4852991.335)],
 '1188205607': [(12956814.39, 4862676.085),
  (12956819.4, 4862673.325),
  (12956808.38, 4862659.96),
  (12947462.66, 4862384.097),
  (12956823.63, 4862674.487)]}

user_id_pair = list(itertools.combinations(arr, 2)) # combine user IDs in pairs (combinations: 3 users * 2 / 2)

for i in range(len(user_id_pair)):
    user_id_1 = user_id_pair[i][0] # get the first user_id from the pair
    user_id_2 = user_id_pair[i][1] # get the second user_id from the pair

    x = arr[user_id_1] # assign the coordinate list corresponding to user_id_1 to x
    y = arr[user_id_2] # assign the coordinate list corresponding to user_id_2 to y

    distance, path = fastdtw(x, y, dist=euclidean) # calculate dtw
    print(distance)
"""

user_id_pair = list(itertools.combinations(user_coor_dict, 2)) # combine user_id in 6,105 pairs (combinations: 111 users * 110 / 2)

id1 = []
id2 = []
dtw_list = []

for i in range(len(user_id_pair)):
    user_id_1 = user_id_pair[i][0] # get the first user_id from the pair
    user_id_2 = user_id_pair[i][1] # get the second user_id from the pair

    x = user_coor_dict[user_id_1] # assign the coordinate list corresponding to user_id_1 to x
    y = user_coor_dict[user_id_2] # assign the coordinate list corresponding to user_id_2 to y

    distance, path = fastdtw(x, y, dist=euclidean) # calculate dtw

    id1.append(user_id_1)
    id2.append(user_id_2)
    dtw_list.append(distance)

    out_file.write(f"{id1[i]}\t{id2[i]}\t{dtw_list[i]}\n")


# Q2: Which two users have the largest dtw distance value in the sample set? Plot the check-in points of these two users as polylines on a map. What spatial patterns can you observe?
df = pd.read_csv('weibo_subset_dtw_dist.txt', sep = '\t', names=['id1', 'id2', 'dtw_dist'], header = 0)
df.sort_values('dtw_dist', ascending = False) #id: 1045049335, id2: 1074028031, dtw_dist: 15091338.2966096

largest_dtw = pd.read_csv('weibo_users_subset.txt', sep = '\t')
largest_dtw = largest_dtw.loc[(largest_dtw['UID'] == 1045049335) | (largest_dtw['UID'] == 1074028031), :]
largest_dtw.to_csv('largest_dtw.csv', index = False)

# convert point to line
largest_lines = largest_dtw.groupby('UID').apply(lambda row: LineString(zip(row.NEW_LON, row.NEW_LAT)))
largest_gdf = gpd.GeoDataFrame({'UID': largest_lines.index, 'geometry': largest_lines.values}, columns = ['UID', 'geometry'])
largest_gdf.to_file('largest_lines.shp')


# Q3: Which two users have the smallest dtw distance value in the sample set? Plot the check-in points of these two users as polylines on a map. What spatial patterns can you observe?
df.sort_values('dtw_dist', ascending = True) #id: 1053568140, id2: 1147562814, dtw_dist: 13867.3223354688

smallest_dtw = pd.read_csv('weibo_users_subset.txt', sep = '\t')
smallest_dtw = smallest_dtw.loc[(smallest_dtw['UID'] == 1053568140) | (smallest_dtw['UID'] == 1147562814), :]
smallest_dtw.to_csv('smallest_dtw.csv', index=False)

# convert point to line
smallest_lines = smallest_dtw.groupby('UID').apply(lambda row: LineString(zip(row.NEW_LON, row.NEW_LAT)))
smallest_gdf = gpd.GeoDataFrame({'UID': smallest_lines.index, 'geometry': smallest_lines.values}, columns = ['UID', 'geometry'])
smallest_gdf.to_file('smallest_lines.shp')


# Task 2. Write a python function to calculate the Euclidean distance between two trajectories
# Note that Euclidean distance only works when the two users have the same number of points in their trajectory. If the two users have a different number of points, your function should return -1

def euclidean_dist(A, B):
    if len(A) != len (B):
        return -1

    euc_list =[]
    
    for a, b in zip(A, B):
        distance = np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
        euc_list.append(distance)

    avrg_distance = sum(euc_list) / len(euc_list)
    return avrg_distance

"""
# test
A = [(0, 0),(1, 1),(2, 2)]
B = [(0, 0),(1, 2),(3, 4)]
C = [(0, 0), (1, 1)]

print (euclidean_dist(A,B)) # 1.0786893258332633
print (euclidean_dist(A,C)) # -1
"""

id1 = []
id2 = []
euc_list = []

out_file = open("weibo_subset_euc_dist.txt", 'w')
out_file.write("id1\tid2\teuc_dist\n")

for i in range(len(user_id_pair)):
    user_id_1 = user_id_pair[i][0] # get the first user_id from the pair
    user_id_2 = user_id_pair[i][1] # get the second user_id from the pair

    x = user_coor_dict[user_id_1] # assign the coordinate list corresponding to user_id_1 to x
    y = user_coor_dict[user_id_2] # assign the coordinate list corresponding to user_id_2 to y

    distance = euclidean_dist(x, y) # calculate euclidean distance

    id1.append(user_id_1)
    id2.append(user_id_2)
    euc_list.append(distance)

    out_file.write(f"{id1[i]}\t{id2[i]}\t{euc_list[i]}\n")

# Q5 (10 pts): Out of all the user pairs, how many pairs have a valid Euclidean distance (i.e., distance other than -1)?
euc_df = pd.read_csv('weibo_subset_euc_dist.txt', sep = '\t')
euc_df[euc_df['euc_dist'] != -1].shape[0] #468
