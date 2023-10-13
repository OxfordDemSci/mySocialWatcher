# command line arguments
data_dir=$1

# delete logs older than 365 days
# find $data_dir -name "*.log" -type f -mtime +365 -exec rm {} \;
# find $data_dir -name "*.log.gz" -type f -mtime +365 -exec rm {} \;

# compress logs older than 7 days
find $data_dir -name "*.log" -type f -mtime +7 -exec gzip {} \;
