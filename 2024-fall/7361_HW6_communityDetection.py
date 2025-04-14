# Task 1 – Derive the taxi flow network
from collections import Counter
import pandas as pd

def count_flow(infile, col1, col2, outfile):
    flow_count_dict = {} # Create a dictionary to store counts of flows between zone pairs
    id_list = [] # Create a list to store unique zone IDs
    bigfile = open(infile) # Open file
    bigfile.readline() # Skip the header
    for lineno, line in enumerate(bigfile):
        # If the value in column col1 is empty, return the id_list and flow_count_dict
        if line.split(',')[col1] == '':
            return id_list, flow_count_dict

        # Get the zone1_id and zone2_id
        zone1_id = int(line.split(',')[col1])
        zone2_id = int(line.split(',')[col2])
        
        # Skip if the zone1_id and zone2_id are the same
        if zone1_id == zone2_id:
            continue
        
        # Add zone1_id and zone2_id to id_list if it isn't already present
        if zone1_id not in id_list:
            id_list.append(zone1_id)
        if zone2_id not in id_list:
            id_list.append(zone2_id)
        
        # Create pairs of zone1 and zone2
        zone_pair = (zone1_id, zone2_id)
        zone_pair_reverse = (zone2_id, zone1_id)

        # Add the flow count for each zone pair
        if zone_pair in flow_count_dict:
            flow_count_dict[zone_pair] += 1
        elif zone_pair_reverse in flow_count_dict:
            flow_count_dict[zone_pair_reverse] += 1
        else:
            flow_count_dict[zone_pair] = 1 # Assign 1 if the zone pair doesn't exist

        # Print the line number
        print(str(lineno)) 

    # Export outfile
    with open(outfile, "w") as output:
        for k, v in flow_count_dict.items():
            output.write(str(k) + '\t' + str(v) + '\n')
    return id_list, flow_count_dict

# Analyze the New York taxi data
col1 = 7 # pickup zone id
col2 = 8 # drop off zone id
infile = "yellow_tripdata_2020-05.csv"
outfile = "count_pair_jan_2020_pu.txt"
result = count_flow(infile, col1, col2, outfile)

# Creat a dataframe from outfile
result_list = result[1]
result_df = pd.DataFrame(list(result_test.items()), columns=['Points', 'Value'])
result_df[['id1', 'id2']] = pd.DataFrame(result_df['Points'].tolist(), index=df.index)
result_df = result_df[['id1', 'id2', 'Value']]

# Sort ascending or descending frequency by Value
df.sort_values(by='Value', ascending=False) # (74, 75) has the most value of 3036
df.sort_values(by='Value', ascending=True) # (261, 252), (179, 78), (50, 3) etc. have value of 1


# Task 2 – Identify communities 
import igraph as ig
from igraph import *
from extract_flows import count_flow
from functools import reduce # Python3

# Analyze data
col1 = 7
col2 = 8
infile = "yellow_tripdata_2020-05.csv"
outfile = "count_pair_may_2020_pu.txt"

# Get vertices and flow_count_dict by using count_flow function
vertices, flow_count_dict = count_flow(infile, col1, col2, outfile)

g = Graph(directed=False) # Create an undirected graph

# Create lists to store edge and weight
edge_list = []
weight_list = []

# Add the edge and weight lists
for k, v in flow_count_dict.items():
    edge_list.append(k)
    weight_list.append(v)

g.add_vertices(vertices) # Add the vertices to graph

# Convert zone pairs in edge_list to vertex indices in edge_list_index
edge_list_index = []
for pair in edge_list:
    # Find the index of each zone in the vertices list and add the pair of indices to edge_list_index
    edge_list_index.append((vertices.index(pair[0]),vertices.index(pair[1])))
g.add_edges(edge_list_index)

# Assign weight and label the weight
g.es['weight'] = weight_list
g.es['label'] = weight_list

# Detect community using multilevel methodology
community = g.community_multilevel(weights = weight_list)

print (community.membership)

# Write a result file
with open("community_may.txt", "w") as output: # remember to change this file name for May data
    for i in range (len(vertices)):
        output.write(str(vertices[i]) +'\t'+ str(community.membership[i])+'\n')
