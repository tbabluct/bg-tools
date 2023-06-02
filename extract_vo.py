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

    monolithic_filename = bag_file_name + "vo.monolithic"

    logger = aru_py_logger.TransformLogger(monolithic_filename, True)
    print("timestamp,t_x,t_y,t_z,r_x,r_y,r_z,r_w")
    """
    void TransformLogger::WriteToFile(
    const pybind11::EigenDRef<Eigen::MatrixXd> &transform_matrix,
    int64 source_timestamp, int64 dest_timestamp) {
    """

    last_timestamp = 0

    with Reader(bag_file_name) as reader:
        connections = [x for x in reader.connections if x.topic == '/vo/tf2']
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            msg = deserialize_cdr(rawdata, connection.msgtype)

            timestamp = msg.header.stamp.sec + (msg.header.stamp.nanosec // 1_000_000)

            t = msg.transform.translation
            rot = msg.transform.rotation

            transform = np.asarray(
                [[1-2*rot.y**2-2*rot.z**2, 2*rot.x*rot.y-2*rot.z*rot.w, 2*rot.x*rot.z+2*rot.y*rot.w, t.x],
                 [2*rot.x*rot.y+2*rot.z*rot.w, 1-2*rot.x**2-2*rot.z**2, 2*rot.y*rot.z-2*rot.x*rot.w, t.y],
                 [2*rot.x*rot.z-2*rot.y*rot.w, 2*rot.y*rot.z+2*rot.x*rot.w, 1-2*rot.x**2-2*rot.y**2, t.z],
                 [0,0,0,1]])
            # https://en.wikipedia.org/wiki/Rotation_matrix#General_rotations

            logger.write_to_file(transform, last_timestamp, timestamp)
            last_timestamp = timestamp
            print (timestamp, t.x, t.y, t.z, rot.x, rot.y, rot.z, rot.w, sep=",")


if __name__ == "__main__":
    main()