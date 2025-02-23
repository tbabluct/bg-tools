import sys
from rosbags.rosbag1 import Reader
from rosbags.serde import deserialize_cdr, ros1_to_cdr
import png
import numpy as np
import os.path as path
import re
import os

def extract_image_topic_from_bag(bag_file_name, image_topic, output_dir):
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

def find_files(directory, pattern):
    matched_files = []
    regex = re.compile(pattern)

    for root, _, files in os.walk(directory):
        for file in files:
            if regex.search(file):
                matched_files.append(os.path.join(root, file))
    
    return matched_files

def main():
    directory = sys.argv[1]
    pattern = r"zed.*\.bag"
    topics = ["/zed2i/zed_node/left/image_rect_color", "/zed2i/zed_node/right/image_rect_color"]
    OUTPUT_DIR = path.join(directory ,"png/")

    filenames = find_files(directory, pattern)

    for filename in filenames:
        for topic in topics:
            extract_image_topic_from_bag(filename, topic, OUTPUT_DIR)
    

if __name__ == "__main__":
    main()