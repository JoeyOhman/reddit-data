import json
import numpy as np
from matplotlib import pyplot as plt

# New same 30 chars filter with bug fixed that did not update subtree value
# 122.40302084570264
# 198.39463178111404
# 6619206

# New same 30 chars filter
# 81.82738692407105
# 147.87523202704386
# 4952933

# New 10 chars filter
# 76.53238787898867
# 144.13321774457557
# 5312296

# Vanilla
# 101.61933414506521
# 182.76892861294903
# 5962560


def main():
    with open("../data/conversations/conversations_new.jsonl", 'r') as f:
        json_lines = f.readlines()

    json_texts = [json.loads(line)['text'] for line in json_lines]
    for t in json_texts[0:2] + json_texts[1000:1002] + json_texts[50000:50002] + json_texts[-3: -1]:
        print("*" * 100)
        print(t)
    num_words = [len(t.split()) for t in json_texts]
    print(np.mean(num_words))
    print(np.std(num_words))
    print(len(json_texts))
    num_words_filtered = [nw for nw in num_words if nw < 2000]
    counts, bins, _ = plt.hist(num_words_filtered, bins=200)
    plt.show()


if __name__ == '__main__':
    main()
