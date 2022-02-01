import time
import json
from tqdm import tqdm
import datetime as dt
from multiprocessing import Pool

import pandas as pd
import praw
from praw.models import MoreComments


REPLIES_STR = 'replies'


def get_date(created):
    return str(dt.datetime.fromtimestamp(created))


def add_thread_info(thread_dict, submission):
    thread_dict['author'] = "[deleted]" if submission.author is None else submission.author.name
    thread_dict['date'] = get_date(submission.created)
    thread_dict['title'] = submission.title
    thread_dict['body'] = submission.selftext
    thread_dict['shorturl'] = submission.shortlink
    thread_dict['id'] = submission.id
    thread_dict['score'] = submission.score
    thread_dict['num_comments'] = submission.num_comments


def add_comment_info(comment_dict, comment):
    comment_dict['author'] = "[deleted]" if comment.author is None else comment.author.name
    comment_dict['date'] = get_date(comment.created)
    comment_dict['body'] = comment.body
    # if comment.author != "[deleted]":


def get_child_comments(comment, parent_replies_list):
    comments_dict = {}
    if not isinstance(comment, MoreComments):
        # parent_dict.append(comment)
        add_comment_info(comments_dict, comment)
        comments_dict[REPLIES_STR] = []
        reply_list = comments_dict[REPLIES_STR]
    else:
        # comments_dict['comment'] = "MoreCommentsObject"
        reply_list = parent_replies_list

    if not hasattr(comment, REPLIES_STR):
        replies = comment.comments()
    else:
        replies = comment.replies

    for child in replies:
        reply_list.append(get_child_comments(child, reply_list))
        # comments_dict['replies'].append(get_child_comments(child, comments_dict['replies']))

    return comments_dict


# Returns list of top-level comment trees
def get_submission_comments(submission):
    # submission = r.submission(submissionId)
    comments = submission.comments
    # commentsList = []
    # comments_dict = {}
    comments_list = []
    for comment in comments:
        comments_list.append(get_child_comments(comment, comments_list))
    return comments_list


def get_thread_dict(submission):
    thread_dict = {}
    add_thread_info(thread_dict, submission)

    commentList = get_submission_comments(submission)
    # for c in commentList:
    #     print("*" * 30)
    #     print(json.dumps(c, indent=4, ensure_ascii=False))

    thread_dict[REPLIES_STR] = commentList
    return thread_dict


def main():
    reddit = praw.Reddit(user_agent="API-app",
                         client_id="o1Nz-YmBJKHmYGVFGLm6hw", client_secret="DAmhwHfnAZjRWehe-qA9dEcuCKaFhg")

    # url = "https://www.reddit.com/r/sweden/comments/sdslfw/politik_covidtr%C3%A5dar_och_andra_%C3%A4ndringar/"
    # submission = reddit.submission(url=url)
    subreddit_name = 'Sweden'
    subreddit = reddit.subreddit(subreddit_name)
    top_subreddit = subreddit.top(limit=10)

    # comments_processed = 0
    with Pool(processes=10) as pool:
        thread_dict_list = []
        for thread_idx, submission in enumerate(top_subreddit):
            # print(f"Processing thread {thread_idx + 1}, #comments={comments_processed}")
            print(f"Launching job for thread {thread_idx + 1}.")
            # thread_dict = get_thread_dict(submission)
            thread_dict_list.append(pool.apply_async(get_thread_dict, args=[submission]))
            # comments_processed += thread_dict['num_comments']

            # thread_dict_list.append(thread_dict)

        with open(f'data/subreddit_{subreddit_name}.jsonl', 'w') as f:
            for idx, t in tqdm(enumerate(thread_dict_list), total=len(thread_dict_list)):
                thread_dict_list[idx] = t.get()
                json.dump(thread_dict_list[idx], f, ensure_ascii=False)
                f.write("\n")
            f.truncate(f.tell() - 1)

        # for idx, thread_dict in enumerate(thread_dict_list):
        #     json.dump(thread_dict, f, ensure_ascii=False)
        #     if idx < len(thread_dict_list) - 1:
        #         f.write("\n")
    # thread_dict = get_thread_dict(submission)
    # print(json.dumps(thread_dict, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    time_start = time.time()
    main()
    print(f"Time elapsed: {time.time() - time_start}s")
