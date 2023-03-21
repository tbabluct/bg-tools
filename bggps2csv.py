import sys
from rosbags.rosbag1 import Reader
from rosbags.serde import deserialize_cdr, ros1_to_cdr
# From https://ternaris.gitlab.io/rosbags/examples/register_types.html
"""Example: Register type from definition string."""

from rosbags.serde import serialize_cdr
from rosbags.typesys import get_types_from_msg, register_types

def register_nmea_type():
    # Your custom message definition
    # From https://docs.ros.org/en/noetic/api/nmea_msgs/html/msg/Sentence.html
    NMEA_MSG = """
    # A message representing a single NMEA0183 sentence.

    # header.stamp is the ROS Time when the sentence was read.
    # header.frame_id is the frame of reference reported by the satellite
    #        receiver, usually the location of the antenna.  This is a
    #        Euclidean frame relative to the vehicle, not a reference
    #        ellipsoid.
    Header header

    # This should only contain ASCII characters in order to be a valid NMEA0183 sentence.
    string sentence
    """

    register_types(get_types_from_msg(NMEA_MSG, 'nmea_msgs/msg/Sentence'))

    # Type import works only after the register_types call,
    # the classname is derived from the msgtype name above

    # pylint: disable=no-name-in-module,wrong-import-position
    from rosbags.typesys.types import nmea_msgs__msg__Sentence as Sentence  # type: ignore  # noqa

def main():
    register_nmea_type()

    if len(sys.argv) != 2:
        print("Please include path to bag file as first argument")
        exit(1)

    bag_file_name = sys.argv[1]

    print("sec,nanosec,", end="")
    print("nmea_sentence", end="")
    print("\n", end="")

    # /gps/nmea_sentence nmea_msgs/msg/Sentence


    with Reader(bag_file_name) as reader:
        connections = [x for x in reader.connections if x.topic == '/gps/nmea_sentence']
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            msg = deserialize_cdr(ros1_to_cdr(rawdata, connection.msgtype), connection.msgtype)
            print(msg.header.stamp.sec, ",", end="", sep="")
            print(msg.header.stamp.nanosec, ",", end="", sep="")

            print("\"" + msg.sentence + "\"")


if __name__ == "__main__":
    main()