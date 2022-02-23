from typing import List, Dict

import numpy as np
import random


NAMES: List[str] = []
AUTHOR_TO_IDX: Dict[str, int] = {}
INDICES_TAKEN: List[int] = []

# NODE_LIST: List['ThreadNode'] = []


def _setup_name_map():
    global NAMES
    if len(NAMES) == 0:
        with open('tree_to_conversations/first_names.txt', 'r') as f:
            names = f.readlines()
        NAMES = [n.strip() for n in names if len(n.strip()) > 0]


class ThreadTree:
    def __init__(self, json_tree, args):
        self.node_list = []
        _setup_name_map()
        self.root_node = ThreadNode(json_tree, args, self.node_list, parent=None)
        self._normalize_vote_scores()  # min-max normalization to avoid negative values
        self.extracted_seqs = []

    # def extract_conversation(self, num_retries=0):
    def extract_conversation(self):
        global NAMES, AUTHOR_TO_IDX, INDICES_TAKEN
        AUTHOR_TO_IDX = dict()  # each conversation will have a new mapping, even though it's the same thread
        INDICES_TAKEN = []
        # random.shuffle(NAMES)

        best_node = self._find_best_subtree()
        # if num_retries > 10:
        #     return None
        chosen_nodes_list = []
        best_node.get_path(chosen_nodes_list)
        # ids_list = [node.id for node in chosen_nodes_list]
        # if ids_list in self.extracted_seqs:
        #     return None
        # self.extracted_seqs.append(ids_list)
        text_to_return = self._node_list_to_text(chosen_nodes_list)
        for author_name, author_idx in AUTHOR_TO_IDX.items():
            text_to_return = text_to_return.replace(author_name, NAMES[author_idx])
        # clean up! remove all visited nodes with no unvisited children
        # each time a node is removed, make its parent chain's score dirty

        self._clean_up_parent_chain(chosen_nodes_list)

        return text_to_return

    def get_num_leaves(self):
        return sum([1 if len(node.children) == 0 else 0 for node in self.node_list])

    def _normalize_vote_scores(self):
        vote_scores = [node.vote_score for node in self.node_list]
        min_score = min(vote_scores)
        max_score = max(max(vote_scores), 1)
        vote_scores = [(vs - min_score) / max_score for vs in vote_scores]
        for i, node in enumerate(self.node_list):
            node.vote_score = vote_scores[i]
            node.set_node_base_value()

    def _find_best_subtree(self):
        node_subtree_vals = [node.get_subtree_max_value() for node in self.node_list]
        best_idx = np.argmax(node_subtree_vals)
        chosen_node = self.node_list[best_idx]
        return chosen_node

    @staticmethod
    def _clean_up_parent_chain(chosen_nodes_list):
        parents = []
        parent = chosen_nodes_list[0].parent
        while parent is not None:
            parents.append(parent)
            parent = parent.parent

        parents_root_first = list(reversed(parents))
        chosen_nodes_list_and_parents = parents_root_first + chosen_nodes_list
        # Iterate from leaf up to parent
        for node in reversed(chosen_nodes_list_and_parents):
            node.subtree_max_value_dirty = True
            # Delete children that are marked for deletion
            node.children = [child for child in node.children if not child.deleted]
            if len(node.children) == 0 and node.num_visits > 0:
                node.deleted = True

    @staticmethod
    def _node_list_to_text(node_list):
        res = [node.as_text() for node in node_list]
        res = [r for r in res if len(r) > 0]
        return "\n".join(res)


class ThreadNode:
    def __init__(self, json_tree, args, node_list, parent):

        node_list.append(self)
        self.args = args
        self.id = json_tree['id']
        # self.author = self._get_name(json_tree['author'])
        self.author = json_tree['author']
        self.text = self._get_text(json_tree)
        self.max_repeat = args.max_repeat
        # self.visit_penalty = args.val_sub_per_visit
        self.parent = parent
        self.children = [ThreadNode(reply_dict, args, node_list, parent=self) for reply_dict in json_tree['replies']]
        self.num_visits = 0
        self.vote_score = json_tree['score']
        self.base_value = 0
        self.subtree_max_value_dirty = True
        self.subtree_max_value = 0
        # self.subtree_max_value = self.get_subtree_max_value()
        self.deleted = False

    def as_text(self):
        ThreadNode._add_author_mapping(self.author)
        if self.num_visits > self.max_repeat:
            return ""
        if self.parent is None and len(self.children) == 0:
            return self.text
        return self.author + ": " + self.text

    def get_path(self, node_list):
        # add one child to list and increment my own num_visits as I have been chosen
        node_list.append(self)
        self.num_visits += 1
        # self.subtree_max_value_dirty = True
        # self.node_value = self._get_node_value()
        if len(self.children) == 0:
            return
        # child_scores = [child._get_node_value() for child in self.children]
        child_scores = [child.get_subtree_max_value() for child in self.children]
        chosen_child = self.children[np.argmax(child_scores)]
        # node_list.append(chosen_child)
        chosen_child.get_path(node_list)

    def set_node_base_value(self):
        # Prioritize
        # high score: proxy for value of information according to humans
        # long texts: more data for model, scaled down to not take that into account
        # many descendants: indicates more possible paths / larger subtree
        # 1 score = 50 characters = 5 descendants
        self.base_value = self.vote_score * self.args.max_val_for_score + len(self.text) * self.args.val_per_char
        # + self.num_descendants * args.val_per_desc

    def _get_node_value(self):
        # return self.base_value - self.num_visits * self.visit_penalty
        # Don't bother selecting nodes that will be omitted, subtract large value from them
        return self.base_value * (0.5 ** self.num_visits) - (1000 if self.num_visits >= self.args.max_repeat else 0)

    def get_subtree_max_value(self):
        # If values already is calculated just use it
        if not self.subtree_max_value_dirty:
            return self.subtree_max_value

        # Else calculate it and update its status to not dirty
        max_child_subtree_value = 0
        if len(self.children) > 0:
            max_child_subtree_value = max([child.get_subtree_max_value() for child in self.children])
        self.subtree_max_value_dirty = False
        self.subtree_max_value = self._get_node_value() + max_child_subtree_value
        return self.subtree_max_value

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
    def _add_author_mapping(author_name):
        # hsh = (int(hashlib.sha256(author_name.encode('utf-8')).hexdigest()[:16], 16) - 2 ** 63) % len(AUTHOR_TO_NAME)
        # return AUTHOR_TO_NAME[hsh]
        if author_name not in AUTHOR_TO_IDX:
            sampled_idx = None
            for i in range(100):
                sampled_idx = random.randint(0, len(NAMES) - 1)
                if sampled_idx not in INDICES_TAKEN:
                    INDICES_TAKEN.append(sampled_idx)
                    break

            assert sampled_idx is not None
            AUTHOR_TO_IDX[author_name] = sampled_idx
