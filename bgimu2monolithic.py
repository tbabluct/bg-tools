import sys
from rosbags.rosbag1 import Reader
from rosbags.serde import deserialize_cdr, ros1_to_cdr
import numpy as np

#sys.path.insert(0, '/home/torsten/cpp/build/aru_sil_core/lib/')
import aru_py_logger

def main():
    if len(sys.argv) != 3:
        print("Useage: " + sys.argv[0] + " filename.bag filename.monolithic")
        exit(1)

    bag_file_name = sys.argv[1]
    if not bag_file_name.endswith(".bag"):
        print("Useage: " + sys.argv[0] + " filename.bag filename.monolithic")
        exit(1)

    monolithic_filename = sys.argv[2]
    if not monolithic_filename.endswith(".monolithic"):
        print("Useage: " + sys.argv[0] + " filename.bag filename.monolithic")
        exit(1)

    logger = aru_py_logger.ImuLogger(monolithic_filename, True)
    
    with Reader(bag_file_name) as reader:
        connections = [x for x in reader.connections if x.topic == '/imu_topic']
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            msg = deserialize_cdr(ros1_to_cdr(rawdata, connection.msgtype), connection.msgtype)

            timestamp = msg.header.stamp.sec + (msg.header.stamp.nanosec // 1_000_000)

            la = msg.linear_acceleration
            la = np.array([la.x, la.y, la.z], dtype=np.float32)

            av = msg.angular_velocity
            av = np.array([av.x, av.y, av.z], dtype=np.float32)

            logger.write_to_file(timestamp, la, av)
            print (timestamp, la, av)


if __name__ == "__main__":
    main()