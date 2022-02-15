#!/bin/bash

declare -a Subreddits=("NordicCool" "nordic" "ScandinavianInterior")

for sub in "${Subreddits[@]}"; do
  for year in {2018..2021}; do
     echo "------------------------------------------------------------------------------"
     echo "Downloading subreddit $sub for year $year"
     python3 download/pushshift_api.py --subreddit $sub --year $year
     sleep 2
  done
done
