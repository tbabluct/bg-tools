# Usage: extract_gps.py path/to/bag path/to/file.(csv/monolithic)
import sys
from rosbags.rosbag2 import Reader
from rosbags.serde import deserialize_cdr

from rosbags.typesys import get_types_from_msg, register_types
import aru_py_logger
import numpy as np

# Your custom message definition
STR_MSG = """
std_msgs/Header header

uint32 itow
float64 lon
float64 lat
float64 height
float64 hmsl
float32 h_acc
float32 v_acc
float32 vel_n
float32 vel_e
float32 vel_d
float32 speed
float32 g_speed
float32 heading
float32 s_acc
bool pos_cov_valid
bool vel_cov_valid
float32 pos_cov_nn
float32 pos_cov_ne
float32 pos_cov_nd
float32 pos_cov_ee
float32 pos_cov_ed
float32 pos_cov_dd
float32 vel_cov_nn
float32 vel_cov_ne
float32 vel_cov_nd
float32 vel_cov_ee
float32 vel_cov_ed
float32 vel_cov_dd
"""

register_types(get_types_from_msg(STR_MSG, 'ublox_msgs/msg/PosVelCov'))

# Type import works only after the register_types call,
# the classname is derived from the msgtype name above

# pylint: disable=no-name-in-module,wrong-import-position
from rosbags.typesys.types import ublox_msgs__msg__PosVelCov as PosVelCov  # type: ignore  # noqa

def main():
    if len(sys.argv) != 2:
        print ("Usage: extract_gps.py path/to/bag")
        exit(1)

    bag_path = sys.argv[1]
    output_path = bag_path + "ublox_gnss.monolithic"
    logger = aru_py_logger.GnssLogger(output_path, True)

    print("sec,nanosec,lat,lon,alt,vel_n,vel_e,vel_d")
    # create reader instance and open for reading
    with Reader(bag_path) as reader:
        # messages() accepts connection filters
        connections = [x for x in reader.connections if x.topic == "/ublox_gnss"]
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            msg = deserialize_cdr(rawdata, connection.msgtype)
            print(msg.header.stamp.sec, msg.header.stamp.nanosec, end=",", sep=",")
            print(msg.lat, msg.lon, msg.height, sep=",", end=",")
            print(msg.vel_n, msg.vel_e, msg.vel_d, sep=",")

            
            timestamp = msg.header.stamp.sec + (msg.header.stamp.nanosec // 1_000_000)
            logger.set_timestamp(timestamp)
            logger.set_latitude(msg.lat)
            logger.set_longitude(msg.lon)
            logger.set_altitude(msg.height)
            logger.set_height_msl(msg.hmsl)

            vel_ned = np.array([msg.vel_n, msg.vel_e, msg.vel_d], dtype=np.float64)
            logger.set_velocity_ned(vel_ned)

            pos_cov = np.matrix([[msg.pos_cov_nn, msg.pos_cov_ne, msg.pos_cov_nd],
                                    [msg.pos_cov_ne, msg.pos_cov_ee, msg.pos_cov_ed],
                                    [msg.pos_cov_nd, msg.pos_cov_ed, msg.pos_cov_dd]], dtype=np.float64)
            logger.set_pos_covariance(pos_cov)

            vel_cov = np.matrix([[msg.vel_cov_nn, msg.vel_cov_ne, msg.vel_cov_nd],
                                    [msg.vel_cov_ne, msg.vel_cov_ee, msg.vel_cov_ed],
                                    [msg.vel_cov_nd, msg.vel_cov_ed, msg.vel_cov_dd]], dtype=np.float64)
            logger.set_vel_covariance(vel_cov)

            logger.write_to_file()


if __name__ == "__main__":
    main()
