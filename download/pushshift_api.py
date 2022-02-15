import argparse
import json
import time
# from psaw import PushshiftAPI
import datetime as dt
from pathlib import Path
from tqdm import tqdm

from PushshiftAPI_psaw_lib_copy import PushshiftAPI

REQUEST_LIMIT = 1000
SECONDS_PER_DAY = 60 * 60 * 24


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
        if len(json_list) > 0 and json_list[-1].strip() == "":
            json_list = json_list[:-1]
            # f.truncate(f.tell() - 1)
        else:
            with open(file_path, 'a') as f:
                f.write("\n")  # Prepare newline for next append to this file
        counter = len(json_list)
        # "2021-11-12 09:04:37"
        earliest_date = int(dt.datetime.strptime(json.loads(json_list[-1])['date'], '%Y-%m-%d %H:%M:%S').timestamp())
        return earliest_date, counter
    except (FileNotFoundError, IndexError):
        return None


def update_progress_bar(pbar, earliest_received, latest_date):
    pbar.update((latest_date - earliest_received) // SECONDS_PER_DAY)
    pbar.refresh()


def set_progress_bar_complete(pbar, total_time_interval):
    pbar.clear()
    pbar.update(total_time_interval)
    pbar.refresh()


def request_submissions(api, subreddit_name, latest_date, earliest_date, save_dir):
    total_time_interval = (latest_date - earliest_date) // SECONDS_PER_DAY
    pbar = tqdm(total=total_time_interval)
    pbar.set_description("Submissions")
    counter = 0
    res = get_progress_so_far(save_dir + "/submissions.jsonl")
    if res is not None:
        earliest_received, counter = res
        update_progress_bar(pbar, earliest_received, latest_date)
        latest_date = earliest_received
    while latest_date > earliest_date:

        submissions = list(api.search_submissions(before=latest_date,
                                                  after=earliest_date,
                                                  subreddit=subreddit_name,
                                                  filter=['author', 'title', 'selftext',
                                                          'created_utc', 'id', 'score'],
                                                  limit=REQUEST_LIMIT,
                                                  metadata=True))

        if len(submissions) == 0:
            set_progress_bar_complete(pbar, total_time_interval)
            break

        earliest_received = int(submissions[-1].created_utc)
        update_progress_bar(pbar, earliest_received, latest_date)
        latest_date = earliest_received

        new_subs = [submission_to_dict(s) for s in submissions]
        counter += len(new_subs)
        with open(f'{save_dir}/submissions.jsonl', 'a') as f:
            for s in new_subs:
                json.dump(s, f, ensure_ascii=False)
                f.write("\n")

    return counter


def request_comments(api, subreddit_name, latest_date, earliest_date, save_dir):
    total_time_interval = (latest_date - earliest_date) // SECONDS_PER_DAY

    pbar = tqdm(total=total_time_interval)
    pbar.set_description("Comments")

    counter = 0
    res = get_progress_so_far(save_dir + "/comments.jsonl")
    if res is not None:
        earliest_received, counter = res
        update_progress_bar(pbar, earliest_received, latest_date)
        latest_date = earliest_received
    while latest_date > earliest_date:
        comments = list(api.search_comments(before=latest_date,
                                            after=earliest_date,
                                            subreddit=subreddit_name,
                                            filter=['author', 'created_utc', 'id', 'score',
                                                    'parent_id', 'link_id', 'body'],
                                            limit=REQUEST_LIMIT,
                                            metadata=True))

        if len(comments) == 0:
            set_progress_bar_complete(pbar, total_time_interval)
            break

        earliest_received = int(comments[-1].created_utc)
        update_progress_bar(pbar, earliest_received, latest_date)
        latest_date = earliest_received

        new_comments = [comment_to_dict(c) for c in comments]
        counter += len(new_comments)
        with open(f'{save_dir}/comments.jsonl', 'a') as f:
            for c in new_comments:
                json.dump(c, f, ensure_ascii=False)
                f.write("\n")

    return counter


def main(args):
    subreddit_name = args.subreddit
    save_dir = f"data/subreddit_{subreddit_name}/year_{args.year}"
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    # api = PushshiftAPI(max_retries=999, backoff=1)
    api = PushshiftAPI(max_sleep=10, shards_down_behavior=None, detect_local_tz=False, utc_offset_secs=3600)

    latest_date = int(dt.datetime(args.year, 12, 31, 23, 59, 59).timestamp())
    earliest_date = int(dt.datetime(args.year, 1, 1, 0, 0, 0).timestamp())

    n_subs = request_submissions(api, subreddit_name, latest_date, earliest_date, save_dir)
    n_comments = request_comments(api, subreddit_name, latest_date, earliest_date, save_dir)
    print(f"Downloaded: submissions={n_subs}, comments={n_comments}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--subreddit", type=str, default=None,
                        help="The subreddit to request posts from.")
    parser.add_argument("--year", type=int, default=None,
                        help="The year to request posts from.")
    args = parser.parse_args()
    assert args.subreddit is not None
    assert args.year is not None

    start_time = time.time()
    main(args)
    print(f"Time Elapsed: {str(dt.timedelta(seconds=int(time.time() - start_time)))}")
