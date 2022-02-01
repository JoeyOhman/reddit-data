import json
import collections
from langdetect import detect

EX_PATH = "/home/joey/Downloads/reddit_subreddits.ndjson"


def read_jsonl_file(path):
    with open(path, 'r') as json_file:
        json_list = list(json_file)

    json_objects = []
    for json_str in json_list:
        result = json.loads(json_str)
        json_objects.append(result)
        # print(f"result: {result}")
        # print(isinstance(result, dict))

    return json_objects


def filter_by_nordic(json_objects):
    for idx, json_dict in enumerate(json_objects):
        if 'lang' in json_dict and json_dict['lang']:
            lang = json_dict['lang']
        else:
            lang = detect(json_dict['description'])
    langs = [x['lang'] if x['lang'] is not None else detect(x['description']) for x in json_objects]
    counter = collections.Counter(langs)
    print(counter)
    num_nordic = 0
    for lang, n in counter.items():
        if lang in ['sv', 'da', 'nb', 'nn', 'no', 'is']:
            num_nordic += 1
            print(f"{lang}: {n}")

    print(f"Percentage nordic: {(num_nordic / num_total) * 100}%")


# sv: 250
# no: 127
# is: 4
# da: 111
# nn: 3
# Percentage nordic: 0.0005470064524881135%

def main():
    objects = read_jsonl_file(EX_PATH)
    num_total = len(objects)
    for obj in objects:
        if not obj['lang']:
            print("***")
            print(obj['lang'])
            print(obj['description'])

    filter_by_nordic(objects)
    exit()

    exit()
    for obj in objects:
        lang = obj['lang']
        if obj['lang'] not in ['sv', 'da', 'nb', 'nn', 'no', 'is']:
            continue
        # num_nordic += 1
        # print(obj.keys())
        # print(obj['title'])
        # print(obj['description'])
        # print(obj['subreddit_type'])
        # print(obj['lang'])
        # print("***")
    print(num_nordic)


if __name__ == '__main__':
    main()
