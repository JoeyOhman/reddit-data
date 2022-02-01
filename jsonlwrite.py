import json

if __name__ == '__main__':
    d1 = {'hej': "Tjenix"}
    d2 = {'hej': "Hallojsan"}
    dict_list = [d1, d2]
    with open('data/subreddit_Sweden.jsonl', 'w') as f:
        for idx, thread_dict in enumerate(dict_list):
            json.dump(thread_dict, f, ensure_ascii=False)
            # if idx < len(dict_list) - 1:
            f.write("\n")
        f.truncate(f.tell() - 1)