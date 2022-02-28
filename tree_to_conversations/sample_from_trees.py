import argparse
import json
import os
import sys
from pathlib import Path
import time

from ThreadTree import ThreadTree


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
    return conversations


def sample_conversations_from_subreddit(args, subreddit_file):
    trees = read_trees(subreddit_file)
    conversations = []

    for tree in trees:
        convs = sample_conversations(args, tree)
        conversations += [c for c in convs if c is not None and len(c) > args.min_len]

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--in_dir", type=str, default="data/trees_jsonl",
                        help="The path to the jsonl trees.")
    parser.add_argument("--out_dir", type=str, default="data/conversations",
                        help="The output path where samples conversations will be written.")
    parser.add_argument("--percentage_of_leaves", type=float, default=1.0,
                        help="The percentage of potential conversations to sample from each tree.")
    parser.add_argument("--min_len", type=int, default=30,
                        help="The minimum number of characters for a conversation.")
    parser.add_argument("--max_repeat", type=int, default=3,
                        help="The maximum number of times a post can be used, before it is omitted "
                             "(while children can still be used).")
    parser.add_argument("--max_val_for_score", type=float, default=10.0,
                        help="The node value per reddit vote/score.")
    parser.add_argument("--val_per_char", type=float, default=0.05,
                        help="The node value per character, i.e. prefer longer texts.")
    # parser.add_argument("--val_per_desc", type=float, default=0.2,
    #                     help="The node value per descendant in tree.")
    # parser.add_argument("--val_sub_per_visit", type=float, default=10.0,
    #                     help="How much to subtract from a node's value each visit.")
    args = parser.parse_args()

    start_time = time.time()
    main(args)
    print(f"Time elapsed: {time.time() - start_time}s")
