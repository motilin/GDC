import datetime


class Node:

    def __init__(self):
        self.value = None
        self.parent = None
        self.children = set()
        self.leaves = None

    def __eq__(self, other):
        if (other is None) or (type(other) != Node):
            return False
        else:
            self_children_values = [node.value for node in self.children]
            other_children_values = [node.value for node in other.children]
            self_in_other = [value for value in self_children_values if value in other_children_values]
            other_in_self = [value for value in other_children_values if value in self_children_values]
            if (len(self_children_values) == len(other_children_values)) and \
                    (len(self_in_other) == len(other_in_self)) and \
                    (len(self_children_values) == len(self_in_other)) and \
                    (self.value == other.value):
                return True
        return False

    def __hash__(self):
        hash_values = [self.value]
        for child in self.children:
            hash_values.append(child.value)
        hash_tuple = tuple(hash_values)
        return hash(hash_tuple)

    def get_leaves(self):
        self.leaves = Node.get_leaves_helper(self)
        return self.leaves

    @staticmethod
    def get_leaves_helper(root):
        if (root is None) or (type(root) != Node):
            raise TypeError('root should be of type Node')
        elif len(root.children) == 0:
            return [root]
        else:
            leaves = []
            for child in root.children:
                leaves.extend(Node.get_leaves_helper(child))
            return leaves

    def add_child(self, new_node):
        self.children.add(new_node)
        new_node.parent = self

    def get_children(self):
        return self.children

    def get_parent(self):
        return self.parent

    def load_doc(self, doc):
        self.load_doc_helper(self, doc)
        return self

    @staticmethod
    def load_doc_helper(root, doc):

        if doc is None:
            return root

        if type(doc) == list:
            for item in doc:
                Node.load_doc_helper(root, item)
        elif type(doc) == dict:
            for key in doc.keys():
                new_node = Node()
                new_node.value = key
                root.add_child(new_node)
                Node.load_doc_helper(new_node, doc[key])
        elif type(doc) == str:
            new_node = Node()
            new_node.value = doc.strip().lower()
            root.add_child(new_node)
        elif (type(doc) == int) or (type(doc) == bool) or (type(doc) == datetime.datetime):
            new_node = Node()
            new_node.value = doc
            root.add_child(new_node)
        else:
            raise TypeError('unfamiliar variable type')

        return root

    def get_paths(self, key, value=None):
        if self.leaves is None:
            self.leaves = self.get_leaves()
        leaves_of_interest = []
        if value is None:
            for leaf in self.leaves:
                if (leaf.parent is not None) and (leaf.parent.value == key):
                    leaves_of_interest.append(leaf)
        else:
            for leaf in self.leaves:
                if (leaf.value == value) and (leaf.parent is not None) and (leaf.parent.value == key):
                    leaves_of_interest.append(leaf)
        paths = set()
        for leaf in leaves_of_interest:
            pointer = leaf
            path = []
            while pointer.parent is not None:
                path.append(pointer.value)
                pointer = pointer.parent
            path = '.'.join(path[::-1])
            paths.add(path)
        paths = list(paths)
        paths.sort()
        unique_paths = []
        for path in paths:
            unique_paths.append(path.split('.'))
        return unique_paths
