import sys
from rosbags.rosbag1 import Reader
from rosbags.serde import deserialize_cdr, ros1_to_cdr

def main():
    if len(sys.argv) != 2:
        print("Please include path to bag file as first argument")
        exit(1)

    bag_file_name = sys.argv[1]

    print ("sec,nanosec,", end="")
    print("latitude,longitude,altitude,", end="")
    print("position_covariance,position_covariance_type", end="")
    print("\n", end="")


    with Reader(bag_file_name) as reader:
        connections = [x for x in reader.connections if x.topic == '/piksi/navsatfix_best_fix']
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            msg = deserialize_cdr(ros1_to_cdr(rawdata, connection.msgtype), connection.msgtype)
            print(msg.header.stamp.sec, ",", end="", sep="")
            print(msg.header.stamp.nanosec, ",", end="", sep="")

            
            print(msg.latitude, msg.longitude, msg.altitude, end="", sep=",")
            print(",", end="")

            print(msg.position_covariance, msg.position_covariance_type, end="", sep=",")
            print("\n", end="")


if __name__ == "__main__":
    main()