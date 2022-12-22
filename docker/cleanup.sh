# delete logs older than 90 days
find ~/mySocialWatcher/data -name "*.log" -type f -mtime +90 -exec rm {} \;
find ~/mySocialWatcher/data -name "*.log.gz" -type f -mtime +90 -exec rm {} \;

# compress logs older than 7 days
find ~/mySocialWatcher/data -name "*.log" -type f -mtime +7 -exec gzip {} \;
