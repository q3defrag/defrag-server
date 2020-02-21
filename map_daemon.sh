#!/bin/bash
# Runs scraper.py every 30s to update the maps
latest_file=/root/96/latest_map
scraper=/root/96/scraper.py
output=/root/96/defrag-maps/defrag/

while true; do
    latest_map=$(cat $latest_file)
    new_latest_map=$(/usr/bin/python3 $scraper -o $output -p $latest_map | grep DONE | head -n1 | perl -pe "s/.* ([^.]*)...DONE\!/\1/g")
    if [ -n "$new_latest_map" ]; then
        echo "Latest map downloaded: $new_latest_map"
        echo $new_latest_map > $latest_file
    fi
    sleep 30
done
