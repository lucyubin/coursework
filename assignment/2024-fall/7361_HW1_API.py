import pandas as pd
from sodapy import Socrata

client = Socrata("data.austintexas.gov", None)

# Set parameters for date filtering and data retrieval
date_start = "2019-10-11"
date_end = "2019-10-13"
limit = 2000
offset = 0 # “offset” is for pagination. Although it’s set to 0 at the start, it is updated with the “limit” number of records every time the loop runs until no more records are fetched.
data = []

try:
    while True:

        results = client.get("x44q-icha",
                             where=f"(origin_reader_identifier = 'springdale_mlk' OR "
                                   f"origin_reader_identifier = 'Lamar_Blue_Bonnet' OR "
                                   f"origin_reader_identifier = 'lamar_koenig' OR "
                                   f"origin_reader_identifier = 'us183_burleson' OR "
                                   f"origin_reader_identifier = 'burnet_us183') AND "
                                   f"start_time between '{date_start}T00:00:00' and '{date_start}T23:59:59'",
                             limit=limit, offset=offset)  # x44q-icha is the ID of the dataset

        if not results:
            print("No more records to fetch.")
            break
        print(f"Fetched {offset+len(results)} records")  # Debug output
        data.extend(results)
        offset += limit

    if data:
        results_df = pd.DataFrame.from_records(data)
        print("DataFrame created with {} rows.".format(len(results_df)))
        results_df.to_csv("HW1_LEE_Yubin.csv", index=False)
        print("Data saved to CSV.")
    else:
        print("No data retrieved, nothing to save.")
except Exception as e:
    print(f"An error occurred: {e}")

# Ensure client connection is closed properly
finally:
    client.close()
