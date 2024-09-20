# Task 1
import numpy as np
import math

# a function to calculate the rog of a given user
def calculate_rog(lon_list, lat_list):
    mean_x = np.mean(lon_list) # longitudes of mean center
    mean_y = np.mean(lat_list) # latitudes of mean center
    num_pts = len(lon_list) # total number of points
    rog = math.sqrt((sum((lon_list-mean_x)**2)+sum((lat_list-mean_y)**2))/num_pts) # calculate radius of gyration (ROG) based on the given formula
    return rog

'''
x = [1,2,3]
y= [5,2,2]

print (calculate_rog(x,y))
#1.632993161855452
'''
