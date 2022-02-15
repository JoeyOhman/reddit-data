from typing import List, Dict

import numpy as np
import random


NAMES: List[str] = []
AUTHOR_TO_IDX: Dict[str, int] = {}


def _setup_name_map():
    global NAMES, AUTHOR_TO_IDX
    AUTHOR_TO_IDX = dict()  # each conversation will have a new mapping, even though it's the same thread
    if len(NAMES) == 0:
        with open('tree_to_conversations/first_names.txt', 'r') as f:
            names = f.readlines()
        NAMES = [n.strip() for n in names]

    random.shuffle(NAMES)


# TODO: what if text mentions author name, should we try to find this and edit this as well?
class ThreadTree:
    def __init__(self, json_tree, args, root=True):
        if root:
            _setup_name_map()
        self.root = root
        self.id = json_tree['id']
        self.author = self._get_name(json_tree['author'])
        self.text = self._get_text(json_tree)
        self.max_repeat = args.max_repeat
        self.children = [ThreadTree(reply_dict, args, root=False) for reply_dict in json_tree['replies']]
        self.num_descendants = 0
        self.num_descendants = self._get_num_descendants()
        self.base_value = self._get_node_base_value(json_tree['score'], args)
        self.num_extracted = 0
        self.num_visits = 0
        self.extracted_seqs = []

    def as_text(self):
        if self.num_extracted == self.max_repeat:
            return ""
        self.num_extracted += 1
        if self.root and len(self.children) == 0:
            return self.text
        return self.author + ": " + self.text

    def extract_conversation(self, num_retries=0):
        if num_retries > 10:
            return None
        node_list = []
        self._get_path(node_list)
        ids_list = [node.id for node in node_list]
        if ids_list in self.extracted_seqs:
            # New retries will add visits to nodes and may choose another path next time
            # Will also penalize the current node
            return self.extract_conversation(num_retries=num_retries+1)
        self.extracted_seqs.append(ids_list)
        return self._node_list_to_text(node_list)

    def get_num_leaves(self):
        if len(self.children) == 0:
            return 1

        count = 0
        for child in self.children:
            count += child.get_num_leaves()
        return count

    def _get_path(self, node_list):
        # add one child to list and increment my own num_visits as I have been chosen
        node_list.append(self)
        self.num_visits += 1
        if len(self.children) == 0:
            return
        child_scores = [child._get_node_score() for child in self.children]
        chosen_child = self.children[np.argmax(child_scores)]
        # node_list.append(chosen_child)
        chosen_child._get_path(node_list)

    def _get_node_score(self):
        return self.base_value - self.num_visits * 10

    def _get_num_descendants(self):
        if self.num_descendants > 0:
            return self.num_descendants

        descendants = 0
        for child in self.children:
            descendants += 1
            descendants += child._get_num_descendants()
        # self.num_descendants = descendants
        return descendants

    def _get_node_base_value(self, score, args):
        # Prioritize
        # high score: proxy for value of information according to humans
        # long texts: more data for model, scaled down to not take that into account
        # many descendants: indicates more possible paths / larger subtree
        # 1 score = 50 characters = 5 descendants
        return score * args.val_per_score + \
               len(self.text) * args.val_per_char + \
               self.num_descendants * args.val_per_desc

    @staticmethod
    def _node_list_to_text(node_list):
        res = [node.as_text() for node in node_list]
        res = [r for r in res if len(r) > 0]
        return "\n".join(res)

    @staticmethod
    def _get_text(json_tree):
        # is_comment exists only in root level, as children are always comments
        if json_tree.get('is_comment', True):
            return json_tree['body'].strip()
        else:
            title = json_tree['title'].strip()
            body = json_tree['body'].strip()
            sep = "" if title == "" or body == "" else " - "
            return title + sep + body

    @staticmethod
    def _get_name(author_name):
        # hsh = (int(hashlib.sha256(author_name.encode('utf-8')).hexdigest()[:16], 16) - 2 ** 63) % len(AUTHOR_TO_NAME)
        # return AUTHOR_TO_NAME[hsh]
        if author_name not in AUTHOR_TO_IDX:
            AUTHOR_TO_IDX[author_name] = random.randint(0, len(NAMES) - 1)

        return NAMES[AUTHOR_TO_IDX[author_name]]
