import pandas as pd
import datetime
import time
import urllib.request

def get_df():
    """
    Required internet access, extract the data from the internet and return as pandas.Dataframe format object
        """
    # split the data line by line
    url = "http://weatherlink.com/webdl.php?timestamp=0&user=001D0A01071F&pass=26782678&apiToken=DE62B85A508D499B82E0087863295F5A&action=data"

    response = urllib.request.urlopen(url)
    hex_list = response.read()
    hex_lines = [hex_list[x:x+52] for x in range(0, len(hex_list), 52)]

    # create dataframe format
    columns_list = ["Datetime", "Date Stamp", "Time Stamp", "Outside Temperature", "High Out Temperature", "Low Out Temperature", "Rainfall", "High Rain Rate", "Barometer", "Solar Radiation", "Number of Wind Samples", "Inside Temperature", "Inside Humidity", "Outside Humidity",
                    "Average Wind Speed", "High Wind Speed", "Direction of Hi Wind Speed", "Prevailing Wind Direction", "Average UV", "ET", "Invalid data", "Soil Moistures", "Soil Temperatures", "Leaf Wetnesses", "Extra Temperatures", "Extra Humidity", "Reed Closed", "Reed Opened"]
    rows_list = []
    row_dict = {el:0 for el in columns_list}

    # process all the lines and fill it into df

    # list, offset, size
    def b2i(l, o, s): return int.from_bytes(l[o:o+s], byteorder="little")

    def extract_line(l):
        """
        @description: extract all the infomation of one complete line
        @return: dataframe type object with one row
        """
        data = 0

        # Date Stamp
        d = b2i(l, 0, 2)
        yr = int(d/512)
        month = int((d-512*yr)/32)
        day = int(d-(512*yr)-(month*32))
        row_dict["Date Stamp"] = datetime.date(yr+2000, month, day)

        # Time Stamp
        d = b2i(l, 2, 2)
        row_dict["Time Stamp"] = datetime.time(
            int(d/100), int(d-int(d/100)*100))

        # Datetime
        row_dict["Datetime"] = datetime.datetime.combine(
            row_dict["Date Stamp"], row_dict["Time Stamp"])

        row_dict["Outside Temperature"] = b2i(l, 4, 2) / 10  # in F

        row_dict["High Out Temperature"] = b2i(l, 6, 2) / 10  # in F

        row_dict["Low Out Temperature"] = b2i(l, 8, 2) / 10  # in F

        # number of rain clicks over the archive period
        row_dict["Rainfall"] = b2i(l, 10, 2)

        row_dict["High Rain Rate"] = b2i(l, 12, 2)  # rain clicks/hour

        row_dict["Barometer"] = b2i(l, 14, 2) / 1000  # in Hg

        row_dict["Solar Radiation"] = b2i(l, 16, 2)  # in W/m**2

        row_dict["Number of Wind Samples"] = b2i(l, 18, 2)

        row_dict["Inside Temperature"] = b2i(l, 20, 2) / 10  # F

        row_dict["Inside Humidity"] = b2i(l, 22, 1)

        row_dict["Outside Humidity"] = b2i(l, 23, 1)

        row_dict["Average Wind Speed"] = b2i(l, 24, 1)  # in MPH

        row_dict["High Wind Speed"] = b2i(l, 25, 1)  # in MPH

        row_dict["Direction of Hi Wind Speed"] = b2i(l, 26, 1)

        row_dict["Prevailing Wind Direction"] = b2i(l, 27, 1)

        row_dict["Average UV"] = b2i(l, 28, 1)  # UV index

        row_dict["ET"] = b2i(l, 29, 1)  # in (in/1000)

        row_dict["Invalid data"] = b2i(l, 30, 1)

        row_dict["Soil Moistures"] = b2i(l, 31, 4)  # in CentiBars

        row_dict["Soil Temperatures"] = b2i(l, 35, 4) + 90  # in F

        row_dict["Leaf Wetnesses"] = b2i(l, 39, 4)  # Range is 0 – 15

        row_dict["Extra Temperatures"] = b2i(l, 43, 2) + 90  # in F

        row_dict["Extra Humidity"] = b2i(l, 45, 2)

        row_dict["Reed Closed"] = b2i(l, 47, 2)

        row_dict["Reed Opened"] = b2i(l, 49, 2)

        rows_list.append(row_dict.copy())

    for line in hex_lines:
        extract_line(line)
    df = pd.DataFrame(rows_list)

    return df

if __name__ == "__main__":
    start = time.time()
    get_df().to_csv("webdl.csv", index=None)
    print("Time used: ", time.time() - start)