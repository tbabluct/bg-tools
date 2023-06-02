import sys
from rosbags.rosbag2 import Reader
from rosbags.serde import deserialize_cdr
import numpy as np

#sys.path.insert(0, '/home/torsten/cpp/build/aru_sil_core/lib/')
import aru_py_logger

def main():
    if len(sys.argv) != 2:
        print("Useage: " + sys.argv[0] + " path/to/bag/")
        exit(1)

    bag_file_name = sys.argv[1]

    monolithic_filename = bag_file_name + "imu_topic.monolithic"

    logger = aru_py_logger.ImuLogger(monolithic_filename, True)
    print("timestamp,la_x,la_y,la_z,av_x,av_y,av_z")

    with Reader(bag_file_name) as reader:
        connections = [x for x in reader.connections if x.topic == '/imu_topic']
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            msg = deserialize_cdr(rawdata, connection.msgtype)

            timestamp = msg.header.stamp.sec + (msg.header.stamp.nanosec // 1_000_000)

            la = msg.linear_acceleration
            la = np.array([la.x, la.y, la.z], dtype=np.float32)

            av = msg.angular_velocity
            av = np.array([av.x, av.y, av.z], dtype=np.float32)

            logger.write_to_file(timestamp, la, av)
            print (timestamp, la[0], la[1], la[2], av[0], av[1], av[2], sep=",")


if __name__ == "__main__":
    main()