# reddit-data

This repository is used for downloading reddit data with the pushshift API and parsing/reformatting it. 

1. `pip install -r requirements.txt`
2. Fill in subreddit space-separated array of strings in `request_subreddits.sh` 
3. `./request_subreddits.sh`
4. If any crashes occur, simply let it run to completion and rerun the command. The python script will check for any progress done and continue from there. On rare occasions the download freezes and must be restarted. The easiest way to recognize this at the moment is to see if the commandline indicates progress or if the current data file has been modified recently.
5. The bash script runs one python script per (subreddit, year)-tuple. The tqdm bar illuistrates the progress in terms of #days of the year fetched.

The resulting data is within the `data` directory.
