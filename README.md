# reddit-data
This repository is used for downloading reddit data with the pushshift API and parsing/reformatting it.

`pip install -r requirements.txt`

## Fetching and formatting data

### Download through Pushshift API

Downloading takes time, large subreddits, e.g. /r/sweden can take many hours. 

1. Fill in subreddit space-separated array of strings in `request_subreddits.sh` 
2. `./request_subreddits.sh`
3. If any crashes occur, simply let it run to completion and rerun the command. The python script will check for any progress done and continue from there. On rare occasions the download freezes and must be restarted. The easiest way to recognize this at the moment is to see if the commandline indicates progress or if the current data file has been modified recently.
4. The bash script runs one python script per (subreddit, year)-tuple. The tqdm bar illuistrates the progress in terms of #days of the year fetched.

The resulting data is within the `data` directory.

### Raw API data -> JSON Trees
1. `./parse_to_trees.sh`
2. Trees are found in `data/trees_jsonl/`

### JSON Trees -> conversations

Conversation paths can be extracted in many ways from the tree. We have here attempted to write heuristics for selecting nodes to include. Each extraction starts in the root node and scores each child node based on the reddit votes, the text length, and the total number of descendants. Each of these are multiplied with a weight that can be specified as an argument. During tree traversal, the number of visits in a node is kept track of, to encourage visiting new nodes even though their node value is lower. 

The total number of unique paths/conversations that can be extracted equals the number of leaves in the tree. 

Reddit usernames are consistently mapped to random first names found in `trees_to_conversations/first_names.txt`. The name list is a collection of common Swedish, Norwegian, Danish, and Icelandic names.

#### Argument explanation
* `INPUT_TREES_DIR`: Path to jsonl-trees directory
* `OUT_DIR`: Path to directory which output file will be written to
* `PERCENTAGE_OF_LEAVES_TO_SAMPLE`: How many conversations to extract, as percentage of leaves in tree
* `MIN_LEN`: Minimum length of conversations in characters. Shorter conversations are omitted
* `MAX_REPEAT_OF_NODE`: Maximum number of times a nodes text can be included in a conversation. In practice this means that for paths found after this number, the upper nodes that has been used this many times, will be omitted while the lower nodes forms an independent conversation sample.
* `VAL_PER_SCORE`: How much each reddit vote/score is valued when traversing tree (prioritize popular reddit posts)
* `VAL_PER_CHAR`: How much each character is valued when traversing (prioritize longer posts)
* `VAL_PER_DESCENDANT`: How much the number of descendants is valued when traversing (prioritize posts with large sub-trees) 
* `VAL_SUB_PER_VISIT`: How much to subtract from a node score each time it is visited (prioritize new nodes)

1. Setup arguments in script `./sample_conversations.sh` and run it.
2. Resulting conversations are found in the specified out dir as one long `.jsonl` file.


## Potential issues / TODOs

### Data acquisition
1. Not all shards of the Pushshift API are up at all times. Some subreddit time periods had ~10% shards down which means some data is lost. Information about shards are included when downloading data, but omitted when creating the JSON trees.
2. The current data spans [2006-2021], some data should be available for 2022 as well. It is unlikely that there is a point to try and fetch data prior to 2006.

### Formatting

1. How to format the conversations better? How to handle newlines to easily distinguish between posts?
2. Submissions (not replies, but OP post), contain a title and a body. How should this be formatted? Current separator is dash: "title - body"
3. Author names are changed, with no respect to language, e.g. Icelandic names can show up in Swedish language and vice versa.
4. Author names are only changed in the author name field, i.e. when author names are mentioned in the text. They will refer to actual author names instead of the new names. This could be fixed with another scan through the data and replaced.
