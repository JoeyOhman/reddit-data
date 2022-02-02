from typing import Optional, Any


# TODO: Handle comments hanging loose? e.g. parent submission/comment is not present
# TODO: Write results to file, in jsonl with trees or efficient format? Probably jsonl trees!
class SubmissionTree:
    def __init__(self, submissions, comments):
        self.submissions = {data_dict['id']: Node(data_dict) for data_dict in submissions}
        self.comments = {data_dict['id']: Node(data_dict) for data_dict in comments}

        for comment_id, comment_node in self.comments.items():
            parent_node = comment_node.get_parent(self.submissions, self.comments)
            if parent_node is not None:
                parent_node.add_child(comment_node)

        for submission_id, submission_node in self.submissions.items():
            submission_node.print_children()
            print("*" * 70)


class Node:
    def __init__(self, data_dict):
        self.data_dict = data_dict
        self.id = data_dict['id']
        self.children = []
        # self.is_comment = is_comment
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
            c.print_children(indent+1)
