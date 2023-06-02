# Usage: extract_gps.py path/to/bag path/to/file.(csv/monolithic)
import sys
from rosbags.rosbag2 import Reader
from rosbags.serde import deserialize_cdr

def main():
    if len(sys.argv) != 3:
        print ("Usage: extract_gps.py path/to/bag path/to/file.(csv/monolithic)")
        exit(1)

    bag_path = sys.argv[1]
    output_path = sys.argv[2]

    if output_path.endswith(".monolithic"):
        output_type = "monolithic"
    elif output_path.endswith(".csv"):
        output_type = "csv"
    else:
        exit(1)

    print("sec,nanosec,lat,lon")
    # create reader instance and open for reading
    with Reader(bag_path) as reader:
        # messages() accepts connection filters
        connections = [x for x in reader.connections if x.topic == "/garmin_gps_fix"]
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            msg = deserialize_cdr(rawdata, connection.msgtype)
            print(msg.header.stamp.sec, msg.header.stamp.nanosec, end=",", sep=",")
            print(msg.latitude, msg.longitude, sep=",")


if __name__ == "__main__":
    main()
