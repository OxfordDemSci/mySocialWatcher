#!/bin/bash

# command line arguments
data_dir=$1

# delete temporary holds older than 7 days
find $data_dir -name "*_temp.txt" -type f -mtime +7 -delete;