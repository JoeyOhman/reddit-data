import argparse
import json
from pathlib import Path

DATA_PATH = "data/trees_jsonl"


def get_property(json_tree, prop):
    prop_str = json_tree[prop]
    if len(prop_str.strip()) > 0:
        return prop_str + "\n"
    else:
        return ""


def tree_to_raw_text(json_tree):
    raw_text = ""
    # raw_text += json_tree['author'] + "\n"
    raw_text += get_property(json_tree, 'author')
    if not json_tree.get('is_comment', True):
        # raw_text += json_tree['title'] + "\n"
        raw_text += get_property(json_tree, 'title')
    raw_text += get_property(json_tree, 'body')
    for reply in json_tree['replies']:
        raw_text += tree_to_raw_text(reply)
    return raw_text


def write_trees_as_raw_text(file_name, json_trees):
    out_dir = "data/raw_text"
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    with open(f"{out_dir}/{file_name}", 'w') as f:
        for json_tree in json_trees:
            f.write(tree_to_raw_text(json_tree))


def main(args):
    file_name = f"subreddit_{args.subreddit}_{args.year}.jsonl"
    with open(DATA_PATH + f"/{file_name}", 'r') as json_file:
        json_list = list(json_file)

    json_trees = []
    for json_str in json_list:
        json_dict = json.loads(json_str)
        json_trees.append(json_dict)

    write_trees_as_raw_text(file_name.replace("jsonl", "txt"), json_trees)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--subreddit", type=str, default="Sweden",
                        help="The subreddit to request posts from.")
    parser.add_argument("--year", type=int, default=2021,
                        help="The year to request posts from.")
    args = parser.parse_args()

    main(args)
