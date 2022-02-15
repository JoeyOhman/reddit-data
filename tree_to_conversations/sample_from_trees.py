import argparse
import json
import os
import sys
# from collections import Counter
from pathlib import Path

from ThreadTree import ThreadTree

# DATA_PATH = "data/trees_jsonl"
# subreddit_path = DATA_PATH + "/subreddit_uppsala.jsonl"


# PERCENTAGE_OF_LEAVES = 0.5
# ONLY_KEEP_LONGER_THAN = 30


def read_trees(file_path):
    with open(f"{file_path}", 'r') as json_file:
        json_list = list(json_file)
    json_trees = []
    for json_str in json_list:
        json_dict = json.loads(json_str)
        json_trees.append(json_dict)
    return json_trees


def sample_conversations(args, tree):
    thread_tree = ThreadTree(tree, args)
    num_leaves = thread_tree.get_num_leaves()  # equals number of paths from root to leaf

    conversations = []
    num_samples = max(int(num_leaves * args.percentage_of_leaves), 1)
    for i in range(num_samples):
        conversation = thread_tree.extract_conversation()
        if conversations is not None:
            conversations.append(conversation)
    # conversation = thread_tree.extract_conversation()
    # return num_leaves, conversations
    return conversations


def sample_conversations_from_subreddit(args, subreddit_file):
    trees = read_trees(subreddit_file)
    conversations = []
    # num_leaves_list = []
    for tree in trees:
        # num_leaves, convs = sample_conversations(args, tree)
        convs = sample_conversations(args, tree)
        conversations += [c for c in convs if c is not None and len(c) > args.min_len]
        # num_leaves_list.append(num_leaves)

    # print(Counter(num_leaves_list))
    # print(len(conversations))
    # print(conversations[2])
    return conversations


def main(args):
    sys.setrecursionlimit(10000)
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    out_file = args.out_dir + "/conversations.jsonl"
    subreddit_files = [os.path.join(args.in_dir, name) for name in os.listdir(args.in_dir)]
    subreddit_files = [name for name in subreddit_files if "subreddit_" in name and ".jsonl" in name]
    subreddit_files = sorted(subreddit_files)

    if os.path.exists(out_file):
        os.remove(out_file)
    for subreddit_file in subreddit_files:
        print("Extracting conversations from", subreddit_file)
        convs = sample_conversations_from_subreddit(args, subreddit_file)
        with open(out_file, 'a') as f:
            for idx, c in enumerate(convs):
                c_dict = {"text": c}
                json.dump(c_dict, f, ensure_ascii=False)
                f.write("\n")
                # if not (subreddit_file == subreddit_files[-1] and idx == len(convs) - 1):
                    # f.write("\n")
        # exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_dir", type=str, default="data/trees_jsonl",
                        help="The path to the jsonl trees.")
    parser.add_argument("--out_dir", type=str, default="data/conversations",
                        help="The output path where samples conversations will be written.")
    parser.add_argument("--percentage_of_leaves", type=float, default=0.5,
                        help="The percentage of potential conversations to sample from each tree.")
    parser.add_argument("--min_len", type=int, default=20,
                        help="The minimum number of characters for a conversation.")
    parser.add_argument("--max_repeat", type=int, default=3,
                        help="The maximum number of times a post can be used, before it is omitted "
                             "(while children can still be used).")
    parser.add_argument("--val_per_score", type=float, default=1.0,
                        help="The node value per reddit vote/score.")
    parser.add_argument("--val_per_char", type=float, default=0.02,
                        help="The node value per character, i.e. prefer longer texts.")
    parser.add_argument("--val_per_desc", type=float, default=0.2,
                        help="The node value per descendant in tree.")
    parser.add_argument("--val_sub_per_visit", type=float, default=10.0,
                        help="How much to subtract from a node's value each visit.")
    args = parser.parse_args()
    main(args)
