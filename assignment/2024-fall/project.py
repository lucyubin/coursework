# 1. Data preprocessing
import pandas as pd

# Import bike trip data
bike = pd.read_csv('Austin_MetroBike_Trips_20240916.csv')
bike.head(5) # Display first 5 rows of the bike data

# Select data for the year 2024
bike_2024 = bike[bike['Year'] == 2024] # 141,144 rows
bike_2024['Month'].value_counts() # April 2024 has the most data

# Select data for April 2024
bike_apr_2024 = bike_2024[bike_2024['Month'] == 4] # 33,203 rows

# Import kiosk location data
kiosk = pd.read_csv("Austin_MetroBike_Kiosk_Locations.csv") # 102 rows

# Create a DataFrame with unique checkout kiosk names from the April 2024 data
unique_bike = pd.DataFrame(sorted(bike_apr_2024['Checkout Kiosk'].unique()), columns=['Unique Checkout Kiosk'])

# Create a DataFrame with unique kiosk names from the kiosk data
unique_kiosk = pd.DataFrame(sorted(kiosk['Kiosk Name'].unique()), columns=['Unique Checkout Kiosk'])

# Concatenate the two DataFrames (unique bike kiosks and unique kiosk names)
unique_names = pd.concat([unique_bike, unique_kiosk], axis=1)

# Remove leading/trailing spaces from 'Checkout Kiosk' column
bike_apr_2024['Checkout Kiosk'] = bike_apr_2024['Checkout Kiosk'].str.strip()

# Select relevant columns for analysis
bike_apr_2024 = bike_apr_2024[['Trip ID', 'Checkout Date', 'Checkout Time', 'Checkout Kiosk', 'Return Kiosk', 'Trip Duration Minutes']]

# Replace ' & ' with '/' in the 'Kiosk Name' column of the kiosk data
kiosk['Kiosk Name'] = kiosk['Kiosk Name'].str.replace(' & ', '/', regex=False)

# Create a dictionary for specific replacements in the 'Kiosk Name' column
replacement_dict = {
    'Capitol Station / Congress/11th' : '11th/Congress @ The Texas Capitol',
    'State Capitol Visitors Garage @ San Jacinto/12th' : '12th/San Jacinto @ State Capitol Visitors Garage',
    '13th/Trinity' : '13th/Trinity @ Waterloo Greenway',
    'Guadalupe/21st' : '21st/Guadalupe',
    '21st/Speedway @PCL' : '21st/Speedway @ PCL',
    '22nd 1/2/Rio Grande' : '22.5/Rio Grande',
    #'' : '23rd/Pearl', # 30.287329976401352, -97.74632802031869 location driven from app
    'Nueces/26th' : '26th/Nueces',
    'Rio Grande/28th' : '28th/Rio Grande',
    'City Hall / Lavaca/2nd' : '2nd/Lavaca @ City Hall',
    'Nueces @ 3rd' : '3rd/Nueces',
    'Nueces/3rd' : '3rd/Nueces',
    'Convention Center / 3rd/Trinity' : '3rd/Trinity @ The Convention Center',
    'Lavaca/6th' : '6th/Lavaca',
    'Trinity/6th Street' : '6th/Trinity',
    'West/6th St.' : '6th/West',
    'Red River/8th Street' : '8th/Red River',
    'San Jacinto/8th Street' : '8th/San Jacinto',
    'Henderson/9th' : '9th/Henderson',
    'Palmer Auditorium' : 'Barton Springs/Bouldin @ Palmer Auditorium',
    'Barton Springs @ Kinney Ave' : 'Barton Springs/Kinney',
    'Congress/Cesar Chavez' : 'Cesar Chavez/Congress',
    #'' : 'Dean Keeton/Park Place', # 30.287836617190724, -97.72845870365327
    'East 11th St./San Marcos' : 'East 11th/San Marcos',
    'East 11th St. at Victory Grill' : 'East 11th/Victory Grill',
    'Capital Metro HQ - East 5th at Broadway' : 'East 5th/Broadway @ Capital Metro HQ',
    'Medina/East 6th' : 'East 6th/Medina',
    'East 6th/Pedernales St.' : 'East 6th/Pedernales',
    'East 6th at Robert Martinez' : 'East 6th/Robert T. Martinez',
    'Pfluger Bridge @ W 2nd Street' : 'Electric Drive/Sandra Muraida Way @ Pfluger Ped Bridge',
    'UT West Mall @ Guadalupe' : 'Guadalupe/West Mall @ University Co-op',
    'Lake Austin Blvd @ Deep Eddy' : 'Lake Austin Blvd/Deep Eddy',
    'Lakeshore @ Austin Hostel' : 'Lakeshore/Austin Hostel',
    'Nash Hernandez @ RBJ South' : 'Nash Hernandez/East @ RBJ South',
    #'' : 'One Texas Center', # 30.25767062481796, -97.74897583987295
    'Rainey St @ Cummings' : 'Rainey/Cummings',
    'ACC - Rio Grande/12th' : 'Rio Grande/12th',
    'Riverside @ S. Lamar' : 'Riverside/South Lamar',
    'Long Center @ South 1st/Riverside' : 'South 1st/Riverside @ Long Center',
    'South Congress/Barton Springs at the Austin American-Statesman' : 'South Congress/Barton Springs @ The Austin American-Statesman',
    'Sterzing at Barton Springs' : 'Sterzing/Barton Springs',
    'MoPac Pedestrian Bridge @ Veterans Drive' : 'Veterans/Atlanta @ MoPac Ped Bridge'
}

# Replace the specific values in the 'Kiosk Name' column using the dictionary
kiosk['Kiosk Name'] = kiosk['Kiosk Name'].replace(replacement_dict)

# Select specific columns from the 'kiosk' DataFrame
kiosk = kiosk[['Kiosk Name', 'Lat', 'Lon', 'Number of Docks']]

# Create a DataFrame with additional kiosk information to add
add_kiosk = pd.DataFrame({
    'Kiosk Name': ['23rd/Pearl', 'Dean Keeton/Park Place', 'One Texas Center'],
    'Lat': [30.287329976401352, 30.287836617190724, 30.25767062481796],
    'Lon': [-97.74632802031869, -97.72845870365327, -97.74897583987295]
})

# Concatenate the new kiosks (add_kiosk) to the existing kiosk DataFrame
kiosk = pd.concat([kiosk, add_kiosk], ignore_index=True) # 104 rows

# Drop duplicates based on the 'Kiosk Name' column to keep unique kiosks only
kiosk = kiosk.drop_duplicates(subset='Kiosk Name')
kiosk.to_csv('kiosk.csv', index = False)

# Merge the 'bike_apr_2024' DataFrame with the 'kiosk' DataFrame on 'Checkout Kiosk' and 'Kiosk Name'
merged_in = pd.merge(bike_apr_2024, kiosk, left_on = 'Checkout Kiosk', right_on = 'Kiosk Name', how = 'left')

# Rename columns to distinguish between checkout and return location attributes
merged_in = merged_in.rename(columns={
    'Lat': 'Lat',
    'Lon': 'Lon',
    'Number of Docks' : 'Docs',
})
merged_in = merged_in[['Trip ID', 'Checkout Date', 'Checkout Time', 'Trip Duration Minutes', 'Lat', 'Lon']]

# Merge the 'merged_pre' DataFrame with the 'kiosk' DataFrame again, but now using 'Return Kiosk'
merged = pd.merge(merged_pre, kiosk, left_on = 'Return Kiosk', right_on = 'Kiosk Name', how = 'left')

# Rename columns to distinguish return location attributes
merged = merged.rename(columns={
    'Lat': 'rt_Lat',
    'Lon': 'rt_Lon',
    'Number of Docks' : 'rt_Docs',
})

# Drop duplicate 'Kiosk Name' columns generated during the merge process
merged = merged.drop(columns=['Kiosk Name_x', 'Kiosk Name_y'])
