# delete logs older than 365 days
find ~/mySocialWatcher/data -name "*.log" -type f -mtime +365 -exec rm {} \;
find ~/mySocialWatcher/data -name "*.log.gz" -type f -mtime +365 -exec rm {} \;

# compress logs older than 7 days
find ~/mySocialWatcher/data -name "*.log" -type f -mtime +7 -exec gzip {} \;
