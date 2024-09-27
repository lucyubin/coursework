# TASK 1. Calculate DTW values and interpret the results
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw

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

