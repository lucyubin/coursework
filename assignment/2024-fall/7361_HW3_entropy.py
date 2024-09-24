# Task 1
import numpy as np
import math
import pandas as pd

# a function to calculate the rog of a given user
def calculate_rog(lon_list, lat_list):
    mean_x = np.mean(lon_list) # longitudes of mean center
    mean_y = np.mean(lat_list) # latitude of mean center
    num_pts = len(lon_list) # total number of points
    rog = math.sqrt((sum((lon_list-mean_x)**2)+sum((lat_list-mean_y)**2))/num_pts) # calculate ROG based on the given formula
    return rog

"""
case 1)
x = [1,2,3]
y= [5,2,2]
print (calculate_rog(x,y))
#1.632993161855452

case 2)
x = [1,1,1]
y= [5,5,5]
print (calculate_rog(x,y))
#0.0
"""

out_file = open("weibo_rog.txt", 'w') # open output file
counter = 0

with open('weibo_users.txt') as f:
    file = f.readline() # skip header
    
    # calculate the rog of all users in the provided file
    file = f.readlines()  # read all the lines in the Weibo file
    user_lon_dict = {} # a dictionary that stores the longitudes of all users. Key: user ID, value: a list that stores the longitudes of this user
    user_lat_dict = {} # a dictionary that stores the latitudes of all users.
    user_rog_dict = {} # a dictionary that stores the rog of all users.
    previous_user_id = -1 # track if the current user is the first user
    
    for j in file:
        data =j.strip('\n').split('\t')
        current_user_id = data[0] # get the user id of the current row
        current_user_lon = float(data[1]) # get longitude of the current row
        current_user_lat = float(data[2]) # get latitude of the current row
        
        if current_user_id in user_lon_dict: # if some of this user's lat/lon have been added to the dictionary
            user_lon_dict[current_user_id].append(current_user_lon) # keep adding to the lon list where the key is the user id
            user_lat_dict[current_user_id].append(current_user_lat) # keep adding to the lat list where the key is the user id
        
        else: # if this is a new user
            # create a new key
            user_lon_dict[current_user_id] = []
            user_lat_dict[current_user_id] = []
            # add current lat/lon as the first point of this user
            user_lon_dict[current_user_id].append(current_user_lon)
            user_lat_dict[current_user_id].append(current_user_lat)
            
            if (previous_user_id != -1): # if this is not the first user, it means that the previous user's lat/lon lists are complete
                rog = calculate_rog(user_lon_dict[previous_user_id],user_lat_dict[previous_user_id]) # calculate the ROG of the previous user
                out_file.write(previous_user_id + '\t' + str(rog) + "\n") # write to the output file
        previous_user_id = current_user_id
        counter += 1
        print ('line ' + str(counter) + ' processed')

    print ("done")

# Q1 Some users have a zero ROG value. Why is that?
# Q2. Which user has the largest ROG value in the sample set?
df = pd.read_csv('weibo_rog.txt', sep = '\t', names=['UID', 'ROG'])
df.sort_values('ROG', ascending=False) #user ID 2874720221: 63996.18018586324

largest_rog = pd.read_csv('weibo_users.txt', sep = '\t')
largest_rog = largest_rog.loc[largest_rog['UID'] == 2874720221, :]
largest_rog.to_csv('largest_rog.csv', index=False)

smallest_rog = largest_rog.loc[largest_rog['UID'] == 1277354067, :]
smallest_rog.to_csv('smallest_rog.csv', index=False)


# Task 2
import numpy as np
import math
import pandas as pd

def calculate_entropy(lon_list, lat_list):
    # format the input lon and lat list of coord pairs
    pair_list = [tuple(a) for a in zip(lon_list, lat_list)] # i.e. [1,1,2] and [1,1,1] becomes [(1,1),(1,1),(2,1)]
    # get the unique pairs from a 2D list
    unique_list = list(set(pair_list)) # i.e. [(1,1),(1,1),(2,1)] becomes [[(1,1),(2,1)]]

    # count number of each coordinate pair
    count_list = []
    for pair in unique_list:
        count_list.append(pair_list.count(pair))

    # count total coordinate pairs
    total_pairs = len(pair_list)

    # calculate probability and entropy
    prob = [count / total_pairs for count in count_list]
    entropy = -sum([x * math.log(x, 2) for x in prob])

    return entropy


# calculate the entropy of all users in the provided file
out_file = open("weibo_entropy.txt", 'w') # open output file
counter = 0

with open('weibo_users.txt') as f:
    file = f.readline() # skip header
    
    # calculate the rog of all users in the provided file
    file = f.readlines()  # read all the lines in the Weibo file
    user_lon_dict = {} # a dictionary that stores the longitudes of all users. Key: user ID, value: a list that stores the longitudes of this user
    user_lat_dict = {} # a dictionary that stores the latitudes of all users.
    user_rog_dict = {} # a dictionary that stores the rog of all users.
    previous_user_id = -1 # track if the current user is the first user
    
    for j in file:
        data =j.strip('\n').split('\t')
        current_user_id = data[0] # get the user id of the current row
        current_user_lon = float(data[1]) # get longitude of the current row
        current_user_lat = float(data[2]) # get latitude of the current row
        
        if current_user_id in user_lon_dict: # if some of this user's lat/lon have been added to the dictionary
            user_lon_dict[current_user_id].append(current_user_lon) # keep adding to the lon list where the key is the user id
            user_lat_dict[current_user_id].append(current_user_lat) # keep adding to the lat list where the key is the user id
        
        else: # if this is a new user
            # create a new key
            user_lon_dict[current_user_id] = []
            user_lat_dict[current_user_id] = []
            # add current lat/lon as the first point of this user
            user_lon_dict[current_user_id].append(current_user_lon)
            user_lat_dict[current_user_id].append(current_user_lat)
            
            if (previous_user_id != -1): # if this is not the first user, it means that the previous user's lat/lon lists are complete
                entropy = calculate_entropy(user_lon_dict[previous_user_id],user_lat_dict[previous_user_id]) # calculate the entropy of the previous user
                out_file.write(previous_user_id + '\t' + str(entropy) + "\n") # write to the output file
        previous_user_id = current_user_id
        counter += 1
        print ('line ' + str(counter) + ' processed')
        #print (entropy)
    
    print ("done")

# Q3. Which user has the largest entropy value in the sample set?
df = pd.read_csv('weibo_entropy.txt', sep = '\t', names=['UID', 'entropy'])
df.sort_values('entropy', ascending=False) #user ID 3782788443: 7.477392

largest_en = pd.read_csv('weibo_users.txt', sep = '\t')
largest_en = largest_en.loc[largest_en['UID'] == 3782788443, :]
largest_en.to_csv('largest_en.csv', index=False)

smallest_en = largest_en.loc[largest_en['UID'] == 3254816341, :]
smallest_en.to_csv('smallest_en.csv', index=False)
