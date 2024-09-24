# PART 1
import json
import pandas

def parse_data(input_file, output_file):
    with open(input_file, 'r') as file:
        data = json.load(file)

    with open(output_file, 'w') as out_file:
        out_file.write("Record ID\tDevice Address\tOrigin Identifier\tDestination Identifier\tTravel Time (s)\tSpeed (mph)\n")
        for record in data:
            if int(record['speed_miles_per_hour']) < 45:
                line = f"{record['record_id']}\t{record['device_address']}\t{record['origin_reader_identifier']}\t{record['destination_reader_identifier']}\t{record['travel_time_seconds']}\t{record['speed_miles_per_hour']}\n"
                out_file.write(line)

if __name__ == "__main__":
    input_file = 'sample_bluetooth_records.json'  # Change to your JSON file path
    output_file = 'output_data_less_than_45.txt'  # The output text file name
    parse_data(input_file, output_file)

def calculate_average_speed(input_file, output_csv):
    data = pd.read_csv(input_file, delimiter='\t')
    grouped_data = data.groupby('Origin Identifier')['Speed (mph)'].mean().reset_index()
    grouped_data.to_csv(output_csv, index=False)

if __name__ == "__main__":
    input_file = 'output_data_less_than_45.txt'  # Change to your input file path
    output_csv = 'average_speed_by_origin.csv'   # The output CSV file name
    calculate_average_speed(input_file, output_csv)
  
# PART 2
import csv
from operator import itemgetter
import operator
import time
import heapq
import matplotlib.pyplot as plt

#from itertools import imap
# this file splits the large file into smaller files, and sort each smaller file based on each column defined
def split_sort(file_name, lines_per_file, column):
    lines_per_file = lines_per_file
    #smallfile = None
    small_filename = 'small_file_{}.txt'.format(lines_per_file)
    smallfile = open(small_filename, "w")
    with open(file_name) as bigfile:
        bigfile.readline() # skip header
        for lineno, line in enumerate(bigfile):
            if lineno % lines_per_file == 0 and lineno > 0: # if the number of lines in the current small file reaches the limit, sort it and open a new small file
                if smallfile:
                    small_file_sorted = 'small_file_{}_s.txt'.format(lineno)
                    sort_file(small_filename, small_file_sorted, column)
                    print(small_file_sorted + ' sorted')
                    sorted_file_list.append(small_file_sorted) # add filename of the sorted file to a list
                    smallfile.close()
                small_filename = 'small_file_{}.txt'.format(lineno + lines_per_file)
                smallfile = open(small_filename, "w")
            smallfile.write(line) # write the line into the small file
        if smallfile: # sort and close the last small file
            small_file_sorted = 'small_file_{}_s.txt'.format(lineno)
            sort_file(small_filename, small_file_sorted, column)
            sorted_file_list.append(small_file_sorted)
            print(small_file_sorted + ' sorted')
            smallfile.close()
    return sorted_file_list

def sort_file(infile, outfile, column): # sort a file based on the given column
   reader = csv.reader(open(infile), delimiter=",")
   #next(reader)
   f = open(outfile,'w')
   for line in sorted(reader, key = lambda x: int(itemgetter(column)(x))):
      for item in line:
         f.write("%s\t" % item)
      f.write("\n")

def extract_key(line,key_column):
    """Extract the key column
    """
    return int(line.split('\t')[key_column]) # for example

def merge_sort_files(file_list, key_index) :

    files = map(open, file_list)
    with open("merged.txt", "w") as dest:
        #dest.writelines(heapq.merge(*files, key=extract_key(key_index)))

        decorated = [
            ((extract_key(line,key_index), line) for line in f)
            for f in files] # mark which column each line needs to be sorted based on
        merged = heapq.merge(*decorated) # the star sign allows variable number of arguments passed to the function
        undecorated = map(itemgetter(-1), merged) # get the second item of the merged results, which conresponds to the lines to be merged
        dest.writelines(undecorated)

sort_column = 7
lines_per_file = 50000
sorted_file_list=[]
start_time = time.time()

# yellow_tripdata_2020-01.csv is the large file to be sorted

sorted_file_list = split_sort('yellow_tripdata_2020-01.csv',lines_per_file, sort_column)
print ("merging all sorted files...this may take a few minutes...be patient...")
merge_sort_files(sorted_file_list,sort_column)
end_time = time.time()

print ("The runtime of the entire process is " +str(end_time - start_time)+ " seconds.")


# List of different lines_per_file values
lines_per_file_values = [20000, 30000, 40000, 50000, 60000, 70000, 80000]
sorted_file_list=[] # without this code, the runtime constantly increase
runtimes = []

for lines_per_file in lines_per_file_values:
    print(f"Running with lines_per_file={lines_per_file}...")
    start_time = time.time()

    sorted_file_list = split_sort('yellow_tripdata_2020-01.csv', lines_per_file, 7)
    merge_sort_files(sorted_file_list, 7)

    end_time = time.time()
    runtime = end_time - start_time
    runtimes.append(runtime)
    print(f"Runtime for lines_per_file={lines_per_file}: {runtime} seconds")

# Plotting the results
plt.figure()
plt.plot(lines_per_file_values, runtimes, marker='o')
plt.xlabel('Number of Lines per File')
plt.ylabel('Time (seconds)')
plt.grid(True)
plt.show()
