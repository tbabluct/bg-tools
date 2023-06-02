python extract_imu.py $1 > "${1}imu_topic.csv"
python extract_ublox_gnss.py $1 > "${1}ublox_gnss.csv"