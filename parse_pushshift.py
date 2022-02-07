import argparse
import json
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


def parse_submissions_comments(dir_path):
    submissions = read_file(dir_path + "/submissions.jsonl")
    comments = read_file(dir_path + "/comments.jsonl")
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


def main(args):
    data_dir = f"{DATA_PATH}/subreddit_{args.subreddit}/year_{args.year}"
    out_dir = f"{DATA_PATH}/trees_jsonl"
    out_path = f"{out_dir}/subreddit_{args.subreddit}_{args.year}.jsonl"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    submissions, comments = parse_submissions_comments(data_dir)
    sub_tree = SubmissionTree(submissions, comments)
    tree_dicts = sub_tree.get_trees_as_json_list()
    # print(json.dumps(tree_dicts[0], ensure_ascii=False, indent=4))
    # print(json.dumps(tree_dicts[1], ensure_ascii=False, indent=4))
    # print(json.dumps(tree_dicts[2], ensure_ascii=False, indent=4))
    write_trees_jsonl(out_path, tree_dicts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--subreddit", type=str, default="Sweden",
                        help="The subreddit to request posts from.")
    parser.add_argument("--year", type=int, default=2021,
                        help="The year to request posts from.")
    args = parser.parse_args()

    main(args)
