import bisect
import math


class Leaf:
    def __init__(self, previous_leaf, next_leaf, parent, branching_factor=16):
        self.previous = previous_leaf
        self.next = next_leaf
        self.parent = parent
        self.branching_factor = branching_factor
        self.keys = []
        self.children = [] # (key, value)

    def set(self, key, value):
        index = bisect.bisect_left(self.keys, key)
        if index < len(self.keys) and self.keys[index] == key:
            self.children[index] = value
        else:
            self.keys.insert(index, key)
            self.children.insert(index, value)
            if self.size() == self.branching_factor:
                self.split(math.ceil(self.branching_factor / 2))

    def get(self, key):
        # TODO: speed up get
        index = self.keys.index(key)
        return self.children[index]

    def split(self, index):
        self.next = Leaf(self, self.next, self.parent, self.branching_factor)
        
        self.next.keys = self.keys[index:]
        self.next.children = self.children[index:]
        self.keys = self.keys[:index]
        self.children = self.keys[:index]
        # bubble up
        if self.is_root():
            self.parent = Node(None, None, [self.next.keys[0]], [self, self.next], branching_factor=self.branching_factor)
            self.next.parent = self.parent
        else:
            self.parent.add_child(self.next.keys[0], self.next)
        return self.next

    def remove_item(self, key):
        del_index = self.keys.index(key)
        self.keys.pop(del_index)
        removed_item = self.children.pop(del_index)
        self.balance()
        return removed_item

    def balance(self):
        if not self.is_root() and self.size() < self.branching_factor // 2:
            # Borrow from siblings
            if self.previous is not None and self.previous.size() > self.branching_factor // 2:
                self.keys.insert(0, self.previous.keys.pop(-1))
                self.children.insert(0, self.previous.children.pop(-1))
                self.parent.change_key(self.keys[0], self.keys[0])
            elif self.next is not None and self.next.size() > self.branching_factor // 2: 
                self.keys.insert(-1, self.next.keys.pop(0))
                self.children.insert(-1, self.next.children.pop(0))
                self.next.parent.change_key(self.keys[0], self.next.keys[0])
            # Merge. Always merge left.
            elif self.previous is not None:
                del_key = self.previous.keys[-1]
                self.previous.keys.extend(self.keys)
                self.previous.children.extend(self.children)
                self.parent.remove_child(del_key)
            elif self.next is not None:
                del_key = self.keys[-1]
                self.keys.extend(self.next.keys)
                self.children.extend(self.next.children)
                self.parent.remove_child(del_key)

    def is_root(self):
        return self.parent is None

    def size(self):
        return len(self.children)


class Node:
    def __init__(self, previous_node, next_node, keys, children, parent=None, branching_factor=16):
        self.previous = previous_node
        self.next = next_node
        self.keys = keys # NOTE: must keep keys sorted
        self.children = children # NOTE: children must correspond to parents.
        self.parent = parent
        self.branching_factor = branching_factor
        for child in children:
            child.parent = self

    def set(self, key, value):
        # TODO: speed up finding the right bucket
        for i, k in enumerate(self.keys):
            if key < k:
                self.children[i].set(key, value)
                return
        self.children[i + 1].set(key, value)

    def add_child(self, key, greater_child):
        # Childs keys must all be greater than key
        index = bisect.bisect(self.keys, key)
        self.keys.insert(index, key)
        self.children.insert(index + 1, greater_child)
        # Bubble up if too many children
        if len(self.keys) == self.branching_factor:
            self.split(self.branching_factor // 2)


    def change_key(self, old_key, new_key):
        """Replaces the first key that is greater or equal than
        old_key with new_key or modifies the parent's key so that new_key
        falls within the current node"""
        if new_key < self.keys[0]:
            self.parent.change_key(self.keys[0], new_key)
        for i, k in enumerate(self.keys):
            if k >= old_key:
                self.keys[i] = new_key

    def split(self, index):
        # Sibling has keys greater than the current
        self.next = Node(self, self.next, self.keys[index + 1:], self.children[index + 1:], self.parent)
        split_key = self.keys[index]
        self.keys = self.keys[:index]
        self.children = self.children[:index + 1]

        if self.is_root():
            self.parent = Node(None, None, [split_key], [self, self.next], branching_factor=self.branching_factor)
        else:
            self.parent.add_child(split_key, self.next)
        return self.next

    def remove_item(self, key):
        """Removes item corresponding to key in the tree.
        """
        for i, k in enumerate(self.keys):
            if k >= key:
                self.children[i].remove_item(key)
                return
        return self.children[-1].remove_item(key)

    def remove_child(self, key):
        """Removes first key that is greater that or equal to
        key and the child to the right of that key.
        Returns the removed child.
        """
        removed_child = None
        for i, k in enumerate(self.keys):
            if k >= key:
                self.keys.pop(i)
                removed_child = self.children.pop(i + 1)
                if removed_child.previous is not None:
                    removed_child.previous.next = removed_child.next
                if removed_child.next is not None:
                    removed_child.next.previous = removed_child.previous
                break
        self.balance()
        return removed_child

    def balance(self):
        # Borrow from siblings if necessary
        if not self.is_root() and self.size() < self.branching_factor // 2:
            if self.previous is not None and self.previous.size() > self.branching_factor // 2:
                self.keys.insert(0, self.previous.keys.pop(-1))
                self.children.insert(0, self.previous.children.pop(-1))
                self.parent.change_key(self.keys[0], self.keys[0])
            elif self.next is not None and self.next.size() > self.branching_factor // 2: 
                self.keys.insert(-1, self.next.keys.pop(0))
                self.children.insert(-1, self.next.children.pop(0))
                self.next.parent.change_key(self.keys[0], self.next.keys[0])
            # Merge. Always merge left.
            elif self.previous is not None:
                del_key = self.previous.keys[-1]
                self.previous.keys.extend(self.keys)
                self.previous.children.extend(self.children)
                self.parent.remove_child(del_key)
            elif self.next is not None:
                del_key = self.keys[-1]
                self.keys.extend(self.next.keys)
                self.children.extend(self.next.children)
                self.parent.remove_child(del_key)
        # Make child the root only 1 child
        if self.is_root() and len(self.children) == 1:
            # TODO: make child root of greater tree
            self.children[0].parent = None

    def is_root(self):
        return self.parent is None

    def size(self):
        return len(self.children)
