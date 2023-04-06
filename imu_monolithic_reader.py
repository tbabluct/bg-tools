import sys
import aru_py_logger

def main():

    if len(sys.argv) != 2:
        print("Useage: " + sys.argv[0] + " filename.monolithic")
        exit(1)

    monolithic_filename = sys.argv[1]
    if not monolithic_filename.endswith(".monolithic"):
        print("Useage: " + sys.argv[0] + " filename.monolithic")
        exit(1)

    logger = aru_py_logger.ImuLogger(monolithic_filename, False)

    for i in range(1000):
        print (logger.read_from_file())
        print (logger.end_of_file())

if __name__ == "__main__":
    main()