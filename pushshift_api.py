import argparse
import json
import time
from psaw import PushshiftAPI
import datetime as dt
from pathlib import Path


REQUEST_LIMIT = 1000


def get_date(created):
    return str(dt.datetime.fromtimestamp(created))


def submission_to_dict(sub):
    sub_dict = {
        'id': sub.id if hasattr(sub, 'id') else 'None',
        'date': get_date(sub.created_utc) if hasattr(sub, 'created_utc') else 'None',
        'score': sub.score if hasattr(sub, 'score') else 'None',
        'author': sub.author if hasattr(sub, 'author') else 'None',
        'title': sub.title if hasattr(sub, 'title') else 'None',
        'body': sub.selftext if hasattr(sub, 'selftext') else 'None',
        'shards': sub.shards if hasattr(sub, 'shards') else 'None'
    }
    return sub_dict


def comment_to_dict(com):
    com_dict = {
        'id': com.id if hasattr(com, 'id') else 'None',
        'parent_id': com.parent_id if hasattr(com, 'parent_id') else 'None',
        'link_id': com.link_id if hasattr(com, 'link_id') else 'None',
        'date': get_date(com.created_utc) if hasattr(com, 'created_utc') else 'None',
        'score': com.score if hasattr(com, 'score') else 'None',
        'author': com.author if hasattr(com, 'author') else 'None',
        'body': com.body if hasattr(com, 'body') else 'None',
        'shards': com.shards if hasattr(com, 'shards') else 'None'
    }
    return com_dict


def get_progress_so_far(file_path):
    try:
        with open(file_path, 'r') as f:
            json_list = list(f)
        if json_list[-1].strip() == "":
            json_list = json_list[:-1]
            # f.truncate(f.tell() - 1)
        else:
            with open(file_path, 'a') as f:
                f.write("\n")  # Prepare newline for next append to this file
        counter = len(json_list)
        # "2021-11-12 09:04:37"
        earliest_date = int(dt.datetime.strptime(json.loads(json_list[-1])['date'], '%Y-%m-%d %H:%M:%S').timestamp())
        return earliest_date, counter
    except FileNotFoundError:
        return None

    # return earliest_date, counter


def request_submissions(api, subreddit_name, latest_date, earliest_date, save_dir):
    counter = 0
    res = get_progress_so_far(save_dir + "/submissions.jsonl")
    if res is not None:
        latest_date, counter = res
    while latest_date > earliest_date:
        counter += REQUEST_LIMIT
        if counter % 20000 == 0:
            print(f"total_submissions={counter}")
        submissions = list(api.search_submissions(before=latest_date,
                                                  after=earliest_date,
                                                  subreddit=subreddit_name,
                                                  filter=['author', 'title', 'selftext',
                                                          'created_utc', 'id', 'score'],
                                                  limit=REQUEST_LIMIT,
                                                  metadata=True))

        if len(submissions) == 0:
            break
        earliest_received = int(submissions[-1].created_utc)
        latest_date = earliest_received

        new_subs = [submission_to_dict(s) for s in submissions]

        with open(f'{save_dir}/submissions.jsonl', 'a') as f:
            for s in new_subs:
                json.dump(s, f, ensure_ascii=False)
                f.write("\n")

    with open(f'{save_dir}/submissions.jsonl', 'a') as f:
        f.truncate(f.tell() - 1)


def request_comments(api, subreddit_name, latest_date, earliest_date, save_dir):
    counter = 0
    res = get_progress_so_far(save_dir + "/comments.jsonl")
    if res is not None:
        latest_date, counter = res
    while latest_date > earliest_date:
        counter += REQUEST_LIMIT
        if counter % 20000 == 0:
            print(f"total_comments={counter}")
        comments = list(api.search_comments(before=latest_date,
                                            after=earliest_date,
                                            subreddit=subreddit_name,
                                            filter=['author', 'created_utc', 'id', 'score',
                                                    'parent_id', 'link_id', 'body'],
                                            limit=REQUEST_LIMIT,
                                            metadata=True))

        # print("*" * 50)
        # print(comments[0])
        if len(comments) == 0:
            break
        earliest_received = int(comments[-1].created_utc)
        latest_date = earliest_received

        new_comments = [comment_to_dict(c) for c in comments]
        with open(f'{save_dir}/comments.jsonl', 'a') as f:
            for c in new_comments:
                json.dump(c, f, ensure_ascii=False)
                f.write("\n")

    with open(f'{save_dir}/comments.jsonl', 'a') as f:
        f.truncate(f.tell() - 1)


def main(args):
    subreddit_name = args.subreddit
    save_dir = f"data/subreddit_{subreddit_name}/year_{args.year}"
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    # api = PushshiftAPI(max_retries=999, backoff=1)
    api = PushshiftAPI()

    latest_date = int(dt.datetime(args.year, 12, 31, 23, 59, 59).timestamp())
    earliest_date = int(dt.datetime(args.year, 1, 1, 0, 0, 0).timestamp())

    request_submissions(api, subreddit_name, latest_date, earliest_date, save_dir)
    request_comments(api, subreddit_name, latest_date, earliest_date, save_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--subreddit", type=str, default="Sweden",
                        help="The subreddit to request posts from.")
    parser.add_argument("--year", type=int, default=2021,
                        help="The year to request posts from.")
    parser.add_argument("--month", type=int, default=None,
                        help="The month to request posts from. If not specified, it will request the entire year.")
    args = parser.parse_args()
    assert not args.month, "Not supported, use entire years =)"

    start_time = time.time()
    main(args)
    print(f"Time Elapsed: {time.time() - start_time}")
