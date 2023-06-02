import sys
from rosbags.rosbag2 import Reader

# /imu_topic sensor_msgs/msg/Imu

def main():
    # create reader instance
    with Reader(sys.argv[1]) as reader:
        # topic and msgtype information is available on .connections list
        for connection in reader.connections:
            print(connection.topic, connection.msgtype)

if __name__ == "__main__":
    main()
