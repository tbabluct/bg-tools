import sys
from rosbags.rosbag1 import Reader
from rosbags.serde import deserialize_cdr, ros1_to_cdr
import png
import numpy as np
import os.path as path

def main():
    bag_file_name = sys.argv[1]
    image_topic = sys.argv[2]
    output_dir = sys.argv[3]

    with Reader(bag_file_name) as reader:
        connections = [x for x in reader.connections if x.topic == image_topic]
        for connection, timestamp, rawdata in reader.messages(connections=connections):
            msg = deserialize_cdr(ros1_to_cdr(rawdata, connection.msgtype), connection.msgtype)
    
            print(msg)
            png_filename = image_topic.replace('/', '_') + "_{:d}_{:09d}.png".format(msg.header.stamp.sec, msg.header.stamp.nanosec)
            # row, col, colour
            png_array = np.zeros((msg.height, 3*msg.width), dtype=np.uint8)
            for row_index in range(msg.height):
                png_array[row_index, 2:3*msg.width:3] = msg.data[(row_index * msg.step):(row_index * msg.step) + 4*msg.width:4]
                png_array[row_index, 1:3*msg.width:3] = msg.data[(row_index * msg.step)+1:(row_index * msg.step) + 4*msg.width:4]
                png_array[row_index, 0:3*msg.width:3] = msg.data[(row_index * msg.step)+2:(row_index * msg.step) + 4*msg.width:4]

            writer = png.Writer(msg.width, msg.height, bitdepth=8, greyscale=False)
            with open(path.join(output_dir, png_filename), 'wb') as f:
                writer.write(f, png_array)
    

if __name__ == "__main__":
    main()