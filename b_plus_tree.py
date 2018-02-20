import bisect

from b_plus_node import Leaf, Node


class BPlusTree:
    def __init__(self, branching_factor=16):
        self.branching_factor = branching_factor
        self.leaves = Leaf(None, None, None, branching_factor) # Linked List of leaves
        self.root = self.leaves

    def get(self, key):
        return self.root.get(key)

    def __getitem__(self, key):
        return self.get(key)

    def remove_item(self, key):
        self.root.remove_item(key)
        if type(self.root) is Node and len(self.root.children) == 1:
            self.root = self.root.children[0]

    def __delitem__(self, key):
        return self.remove_item(key)

    def set(self, key, value):
        self.root.set(key, value)
        if self.root.parent is not None:
            self.root = self.root.parent

    def __setitem__(self, key, value):
        return self.set(key, value)

    def size(self):
        result = 0
        leaf = self.leaves
        while leaf is not None:
            result += leaf.size()
            leaf = leaf.next
        return result

    def split(self, key):
        tree = BPlusTree()
        tree.root = Node(None, None, [], [], self.branching_factor)

        current_node = self.root
        new_node = tree.root
        while type(current_node) is Node or type(current_node) is Leaf:
            child_type = type(current_node.children[0])
            split_index = bisect.bisect_left(current_node.keys, key)
            new_node.keys = current_node.keys[:split_index]
            new_node.children = current_node.children[:split_index]
            current_node.keys = current_node.keys[split_index:]
            current_node.children = current_node.children[split_index:]
            if len(current_node.children) == 0:
                break
            # Add new ambiguous node on the split and fix pointers
            if child_type is Node:
                new_node.children.append(Node(new_node.children[-1], None, [], [],
                                              parent=new_node,
                                              branching_factor=new_node.branching_factor))
                new_node.children[-2].next = new_node.children[-1]
                current_node.children[0].previous = None
            elif child_type is Leaf:
                new_node.children.append(Leaf(new_node.children[-1], None, new_node,
                                              branching_factor=new_node.branching_factor))
                new_node.children[-2].next = new_node.children[-1]
                current_node.children[0].previous = None
            # Balance trees
            new_node.balance()
            current_node.balance()
            current_node = current_node.children[0]
            new_node = new_node.children[-1]

        return tree
