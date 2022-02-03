import json

from SubmissionTree import SubmissionTree

# DATA_PATH = "data/subreddit_Spel/year_2020"
DATA_PATH = "data/subreddit_ISKbets/year_2021"


def read_file(path):
    with open(path, 'r') as json_file:
        json_list = list(json_file)

    json_dicts = [json.loads(json_str) for json_str in json_list]
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


def find_parent(submissions, comments, json_dict):
    parent_id = json_dict['parent_id']
    top_level = parent_id[:2] == "t3"
    return submissions[parent_id[3:]] if top_level else comments[parent_id[3:]]


def main():
    submissions, comments = parse_submissions_comments(DATA_PATH)
    sub_tree = SubmissionTree(submissions, comments)


if __name__ == '__main__':
    main()
