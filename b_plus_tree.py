from b_plus_node import Leaf, Node


class BPlusTree:
    def __init__(self, branching_factor=16):
        self.branching_factor = branching_factor
        self.leaves = Leaf(None, None, None, branching_factor) # Linked List of leaves
        self.root = self.leaves
        self.num_items = 0

    def get(self, key):
        return self.root.get(key)

    def __getitem__(self, key):
        return self.get(key)

    def remove_item(self, key):
        self.root.remove_item(key)
        if type(self.root) is Node and len(self.root.children) == 1:
            self.root = self.root.children[0]
        self.num_items -= 1

    def __delitem__(self, key):
        return self.remove_item(key)

    def set(self, key, value):
        self.root.set(key, value)
        if self.root.parent is not None:
            self.root = self.root.parent
        self.num_items += 1

    def __setitem__(self, key, value):
        return self.set(key, value)

    def size(self):
        result = 0
        leaf = self.leaves
        while leaf is not None:
            result += leaf.size()
            leaf = leaf.next
