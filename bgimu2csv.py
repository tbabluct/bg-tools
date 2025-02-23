import sys
from rosbags.rosbag1 import Reader
from rosbags.serde import deserialize_cdr, ros1_to_cdr

def main():
    if len(sys.argv) != 2:
        print("Please include path to bag file as first argument")
        exit(1)

    bag_file_name = sys.argv[1]

    print ("sec,nanosec,", end="")
    print("la_x,la_y,la_z,", end="")
    print("av_x,av_y,av_z", end="")
    print("\n", end="")


    with Reader(bag_file_name) as reader:
        connections = [x for x in reader.connections if x.topic == '/microstrain/imu/data']
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            msg = deserialize_cdr(ros1_to_cdr(rawdata, connection.msgtype), connection.msgtype)
            print(msg.header.stamp.sec, ",", end="", sep="")
            print(msg.header.stamp.nanosec, ",", end="", sep="")

            la = msg.linear_acceleration
            print(la.x, la.y, la.z, end="", sep=",")
            print(",", end="")

            av = msg.angular_velocity
            print(av.x, av.y, av.z, end="", sep=",")
            print("\n", end="")


if __name__ == "__main__":
    main()