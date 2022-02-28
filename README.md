# reddit-data
This repository is used for downloading reddit data with the pushshift API and parsing/reformatting it.

`pip install -r requirements.txt`

A submission node (OP post) contains a title and a body, and replies only a body. The final conversation format is:
```
<Author>: <Title> - <Body>
<Author>: <Body>
<Author>: <Body>
...
```

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

Conversation paths can be extracted in many ways from the tree. We have here attempted to write heuristics for selecting nodes to include. Each node gets a node value that depends on the length of the text and the reddit votes for the comment. Each node then has a max subtree value, which uses information from the maximum path down the subtree for that node. A list of nodes is kept, and the node with the maximum sub tree score is selected each time. The node value is halved each time the node is used for a sample. When a leaf node is used for a sample, it is then deleted from the tree, as there is no point in reusing a leaf, i.e. we only reuse nodes that can act as a context to different children. 

The total number of unique paths/conversations that can be extracted equals the number of leaves in the tree. We extract exactly this number of samples, and filter out samples with too few characters. 

Reddit usernames are consistently mapped to random first names found in `trees_to_conversations/first_names.txt`. The name list is a collection of common Swedish, Norwegian, Danish, and Icelandic names.

#### Argument explanation
* `INPUT_TREES_DIR`: Path to jsonl-trees directory
* `OUT_DIR`: Path to directory which output file will be written to
* `PERCENTAGE_OF_LEAVES_TO_SAMPLE`: How many conversations to extract, as percentage of leaves in tree
* `MIN_LEN`: Minimum length of conversations in characters. Shorter conversations are omitted
* `MAX_REPEAT_OF_NODE`: Maximum number of times a nodes text can be included in a conversation. In practice this means that for paths found after this number, the upper nodes that has been used this many times, will be omitted while the lower nodes forms an independent conversation sample.
* `MAX_VAL_FOR_SCORE`: How much node value can be increased at max for reddit vote/score.
* `VAL_PER_CHAR`: How much each character is valued when traversing (prioritize longer posts)

1. Setup arguments in script `./sample_conversations.sh` and run it.
2. Resulting conversations are found in the specified out dir as one long `.jsonl` file.


## Potential issues / TODOs

### Data acquisition
1. Not all shards of the Pushshift API are up at all times. Some subreddit time periods had ~10% shards down which means some data is lost. Information about shards are included when downloading data, but omitted when creating the JSON trees.
2. The current data spans [2006-2021], some data should be available for 2022 as well. It is unlikely that there is a point to try and fetch data prior to 2006.

### Formatting
3. Author names are changed, with no respect to language, e.g. Icelandic names can show up in Swedish language and vice versa.
5. Author names are changed in the text as well, but what if someone has a common word as their name? Then this will get swapped as well. 
6. To dodge all problems, should we even use author name replacement? One could argue that these random names are actually useful to allow the model to identify and work with usernames.
7. When building trees, it chooses paths with the highest total value, i.e. the longest text sequence. One could instead aim for some target length to encourage many medium long samples instead.
