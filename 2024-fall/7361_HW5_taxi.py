import pandas as pd
from collections import Counter

def percent_by_count(my_list): # calculate the percentage of each unique item
    counter = dict(Counter(my_list))
    p_dict = {k: v / total for total in (sum(counter.values()),) for k, v in counter.items()}
    return p_dict

"""
# example data to test the percent_by_count function
my_list = [1,1,1,2,2,4,5,6,6,6]

print (percent_by_count(my_list))
"""

def cmp_dict(dict1, dict2): # compare the keys and values of two dictionaries
    keys_only_dict1 = []
    keys_only_dict2 = []
    diff_dict = {}

    for key in dict1.keys():
        if key in dict2:
            diff_dict[key] = dict1[key] - dict2[key]
        else:
            keys_only_dict1.append(key)
            diff_dict[key] = dict1[key]

    for key in dict2.keys():
        if not key in dict1:
            keys_only_dict2.append(key)
            diff_dict[key] = -dict2[key]
    return keys_only_dict1, keys_only_dict2, diff_dict

"""
# example data to test the cmp_dict function
dict1= {1:0.2, 2:0.5,3:0.1, 4:0.2}
dict2= {1:0.1, 2:0.5,4:0.1, 5:0.1}

print (cmp_dict(dict1, dict2))
"""

# import csv data and etract the zone ID
jan_csv = pd.read_csv("yellow_tripdata_2020-01.csv")
jan_id = jan_csv['PULocationID'].tolist()

may_csv = pd.read_csv("yellow_tripdata_2020-05.csv")
may_id = may_csv['PULocationID'].tolist()

# create two dictionaries that show the percentages of zones
jan_data = percent_by_count(jan_id)
may_data = percent_by_count(may_id)

# compare two percentages
cmp_may_jan = cmp_dict(may_data, jan_data)
cmp_may_jan2 = cmp_may_jan[2]

with open("diff_jan_may_pu.txt", "w") as file:
    file.write("zone_id\tpercent_diff\n")
    
    for zone_id, percent_diff in cmp_may_jan2.items():
        file.write(f"{zone_id}\t{percent_diff}\n")

# Q. Which taxi zones had the largest decrease in the percentage of taxi pick-ups in May?
cmp_df = pd.read_csv('diff_jan_may_pu.txt', sep = '\t')
cmp_df.sort_values(by = 'percent_diff') #zone_id 161 had -0.03% and the top 3 were 161, 132, and 230

# Q. Which taxi zone had the largest increase in the percentage of taxi pick-ups in May? List the ID of this taxi zone.
cmp_df.sort_values(ascending = False, by = 'percent_diff') #zone_id 137(0.04%)
