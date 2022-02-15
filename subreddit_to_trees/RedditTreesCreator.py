from typing import Optional
from tqdm import tqdm
import html


# TODO: Handle comments hanging loose? e.g. parent submission/comment is not present
# TODO: Write results to file, in jsonl with trees or efficient format? Probably jsonl trees!
class RedditTreesCreator:
    def __init__(self, submissions, comments):
        print("Creating id->Node maps and removing duplicates/deleted")
        deleted_filter = ["[deleted]", "[removed]", "None"]
        self.submissions = {data_dict['id']: Node(data_dict, False) for data_dict in submissions
                            if data_dict['author'] not in deleted_filter
                            and data_dict['title'] not in deleted_filter
                            and data_dict['body'] not in deleted_filter}
        self.comments = {data_dict['id']: Node(data_dict, True) for data_dict in comments
                         if data_dict['author'] not in deleted_filter
                         and data_dict['body'] not in deleted_filter
                         }
        self.comments_no_parent = {}
        print("Connecting nodes to their parents")
        # if tqdm shows a lower number than number of read comments, some duplicates or deleted were removed
        for comment_id, comment_node in tqdm(self.comments.items()):
            parent_node = comment_node.get_parent(self.submissions, self.comments)
            if parent_node is None:
                self.comments_no_parent[comment_node.id] = comment_node
            else:
                parent_node.add_child(comment_node)

    def print_trees(self):
        for submission_id, submission_node in self.submissions.items():
            submission_node.print_children()
            print("*" * 70)

        print("#" * 150)
        for comment_id, comment_node in self.comments_no_parent.items():
            comment_node.print_children()
            print("*" * 70)

    def get_trees_as_json_list(self):
        submission_dicts = []
        for submission_id, submission_node in self.submissions.items():
            json_dict = submission_node.as_json(True)
            submission_dicts.append(json_dict)

        comment_dicts = []
        for comment_id, comment_node in self.comments_no_parent.items():
            json_dict = comment_node.as_json(True)
            comment_dicts.append(json_dict)

        submission_dicts = sorted(submission_dicts, key=lambda x: x['date'])
        comment_dicts = sorted(comment_dicts, key=lambda x: x['date'])

        all_dicts = submission_dicts + comment_dicts
        return all_dicts


class Node:
    def __init__(self, data_dict, is_comment):
        self.data_dict = data_dict
        self.id = data_dict['id']
        self.children = []
        self.is_comment = is_comment
        # self.is_top_level = data_dict['parent_id'] if is_comment else None

    def add_child(self, node):
        self.children.append(node)

    def get_parent(self, submissions, comments) -> Optional['Node']:
        parent_id = self.data_dict['parent_id']
        top_level = parent_id[:2] == "t3"
        try:
            return submissions[parent_id[3:]] if top_level else comments[parent_id[3:]]
        except KeyError:
            return None

    def print_children(self, indent=0):
        print("-" * indent * 4 + repr(self.data_dict['body']))
        for c in self.children:
            c.print_children(indent + 1)

    def as_json(self, root_node):
        """
        json_dict = {
            'id': self.data_dict['id'],
            'date': self.data_dict['date'],
            'author': self.data_dict['author'],
        }
        """
        del self.data_dict['shards']
        if self.is_comment:
            del self.data_dict['parent_id']
            del self.data_dict['link_id']

        self.data_dict['body'] = html.unescape(self.data_dict['body'])
        self.data_dict['author'] = html.unescape(self.data_dict['author'])
        if not self.is_comment:
            self.data_dict['title'] = html.unescape(self.data_dict['title'])

        if root_node:
            self.data_dict['is_comment'] = self.is_comment
        self.data_dict['replies'] = []
        if len(self.children) > 0:
            self.children = sorted(self.children, key=lambda x: x.data_dict['date'])
            for child_node in self.children:
                self.data_dict['replies'].append(child_node.as_json(False))

        return self.data_dict
