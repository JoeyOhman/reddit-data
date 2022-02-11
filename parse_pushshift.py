import argparse
import json
import os
from pathlib import Path

from SubmissionTree import SubmissionTree

DATA_PATH = "data"
# DATA_PATH = "data/subreddit_Spel/year_2021"
# DATA_PATH = "data/subreddit_ISKbets/year_2021"
# DATA_PATH = "data/subreddit_Svenska/year_2021"


def read_file(path):
    with open(path, 'r') as json_file:
        json_list = list(json_file)

    json_dicts = [json.loads(json_str) for json_str in json_list if json_str.strip() != ""]
    # json_dicts = [{json_dict['id']: json_dict} for json_dict in json_dicts]
    # TODO: list to dict, key -> rest of dict
    # json_dicts = {json_dict['id']: json_dict for json_dict in json_dicts}
    # print(json.dumps(json_dicts[0], indent=4, ensure_ascii=False))
    return json_dicts


def read_submissions_comments(dir_path):
    try:
        submissions = read_file(dir_path + "/submissions.jsonl")
    except FileNotFoundError:
        submissions = []

    try:
        comments = read_file(dir_path + "/comments.jsonl")
    except FileNotFoundError:
        comments = []
    # print(json.dumps(comments[0], indent=4, ensure_ascii=False))
    # test_comment = comments['gh47is9']
    # print(json.dumps(test_comment, indent=4, ensure_ascii=False))
    # parent = find_parent(submissions, comments, test_comment)
    # print(json.dumps(parent, indent=4, ensure_ascii=False))
    return submissions, comments

"""
def find_parent(submissions, comments, json_dict):
    parent_id = json_dict['parent_id']
    top_level = parent_id[:2] == "t3"
    return submissions[parent_id[3:]] if top_level else comments[parent_id[3:]]
"""


def write_trees_jsonl(out_path, tree_dicts):
    with open(out_path, 'w') as f:
        for idx, json_dict in enumerate(tree_dicts):
            json.dump(json_dict, f, ensure_ascii=False)
            if idx < len(tree_dicts) - 1:
                f.write("\n")


def process_subreddit(subreddit_dir, out_dir):
    out_path = f"{out_dir}/{subreddit_dir}.jsonl"

    submissions_all, comments_all = [], []
    print("Reading submissions & comments for subreddit", )
    for year in range(2006, 2022):
        data_dir = f"{DATA_PATH}/{subreddit_dir}/year_{year}"
        submissions, comments = read_submissions_comments(data_dir)
        submissions_all += submissions
        comments_all += comments

    print(f"Read {len(submissions_all)} submissions and {len(comments_all)} comments")
    sub_tree = SubmissionTree(submissions_all, comments_all)
    print("Converting nodes into json trees, sorting children lists on date")
    tree_dicts = sub_tree.get_trees_as_json_list()
    # print(json.dumps(tree_dicts[0], ensure_ascii=False, indent=4))
    # print(json.dumps(tree_dicts[1], ensure_ascii=False, indent=4))
    # print(json.dumps(tree_dicts[2], ensure_ascii=False, indent=4))
    print("Writing json trees to jsonl file")
    write_trees_jsonl(out_path, tree_dicts)


def main(args):
    # subreddit_dir = f"{DATA_PATH}/subreddit_{args.subreddit}
    subreddit_dirs = [name for name in os.listdir(DATA_PATH) if os.path.isdir(os.path.join(DATA_PATH, name))]
    subreddit_dirs = [name for name in subreddit_dirs if "subreddit_" in name]
    # print(subreddit_dirs)
    out_dir = f"{DATA_PATH}/trees_jsonl"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for subreddit in subreddit_dirs:
        process_subreddit(subreddit, out_dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--subreddit", type=str, default="Sweden",
                        help="The subreddit to request posts from.")
    # parser.add_argument("--year", type=int, default=2021,
    #                     help="The year to request posts from.")
    args = parser.parse_args()

    main(args)
