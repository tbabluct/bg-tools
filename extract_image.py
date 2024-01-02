import sys
from rosbags.rosbag2 import Reader
from rosbags.serde import deserialize_cdr
import numpy as np
#import cv2
import copy

#sys.path.insert(0, '/home/torsten/cpp/build/aru_sil_core/lib/')
import aru_py_logger

def main():
    if len(sys.argv) != 3:
        print("Useage: " + sys.argv[0] + " path/to/bag/ topic")
        exit(1)

    bag_file_name = sys.argv[1]
    topic_name = sys.argv[2]

    monolithic_left = bag_file_name + topic_name.replace("/", "_") + "_left.monolithic"
    monolithic_right = bag_file_name + topic_name.replace("/", "_") + "_right.monolithic"

    #logger = aru_py_logger.StereoImageLogger(monolithic_filename, True)
    logger_left = aru_py_logger.MonoImageLogger(monolithic_left, True)
    logger_right = aru_py_logger.MonoImageLogger(monolithic_right, True)

    """
    void StereoImageLogger::WriteToFile(
    pybind11::array_t<unsigned char> &image_left,
    pybind11::array_t<unsigned char> &image_right, int64 timestamp)


    """

    with Reader(bag_file_name) as reader:
        connections = [x for x in reader.connections if x.topic == topic_name]
        count = 0
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            msg = deserialize_cdr(rawdata, connection.msgtype)

            timestamp = msg.header.stamp.sec * 1000 + (msg.header.stamp.nanosec // 1_000_000)
            print(timestamp, msg.width, msg.height, msg.encoding, msg.step, len(msg.data))

            # Display full image to test encoding
            img_joint = np.zeros((msg.height, msg.width, 3), dtype="uint8")

            for y in range(msg.height):
                img_joint[y, 0:msg.width, 0] = msg.data[y*msg.step:(y+1)*msg.step:3]
                img_joint[y, 0:msg.width, 1] = msg.data[y*msg.step+1:(y+1)*msg.step+1:3]
                img_joint[y, 0:msg.width, 2] = msg.data[y*msg.step+2:(y+1)*msg.step+2:3]

            if False and count % 15 == 0:
                cv2.imshow("left", img_joint[:, 0:msg.width//2, :])
                cv2.waitKey()
                cv2.imshow("right", img_joint[:, msg.width//2:, :])
                cv2.waitKey()

            #logger.write_to_file(img_joint[:, 0:msg.width//2, :], img_joint[:, msg.width//2:, :], timestamp)
            img_left = copy.deepcopy(img_joint[:, 0:msg.width//2, :])
            img_right = copy.deepcopy(img_joint[:, msg.width//2:, :])
            logger_left.write_to_file(img_left, timestamp)
            logger_right.write_to_file(img_right, timestamp)
            print ("Writing image:", count)
            count += 1


if __name__ == "__main__":
    main()