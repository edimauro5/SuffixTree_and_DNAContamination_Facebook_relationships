from personal_collections.tree import Tree


class SuffixTree(Tree):
    # ------------------------------- nested _Node class -------------------------------

    class _Node:
        def __init__(self, element, mark, parent, depth):
            self._children = {}
            self._element = element
            self._mark = mark
            self._parent = parent
            self._depth = depth

        def _add_child(self, child, key):
            self._children[key] = child

        def _remove_child(self, key):
            self._children.pop(key)

    # ------------------------------- nested implemented Position class -------------------------------

    class Position(Tree.Position):
        def __init__(self, container, node):
            self._node = node
            self._container = container

        def element(self):
            """Return the element stored at this Position."""
            return self._node._element

        def __eq__(self, other):
            """Return True if other is a Position representing the same location."""
            return type(other) is type(self) and other._node is self._node

    # ------------------------------- implemented Tree abstract methods -------------------------------

    def root(self):
        """Return Position representing the alberi's root (or None if empty)."""
        return self._make_position(self._root)

    def parent(self, p):
        """Return Position representing p's parent (or None if p is root)."""
        node = self._validate(p)
        return self._make_position(node._parent)

    def num_children(self, p):
        """Return the number of children that Position p has."""
        node = self._validate(p)
        return len(node._children)

    def children(self, p):
        """Generate an iteration of Positions representing p's children."""
        node = self._validate(p)
        for child in node._children.values():
            yield self._make_position(child)

    def __len__(self):
        """Return the total number of elements in the alberi."""
        return self._size

    # ------------------------------- SuffixTree concrete methods -------------------------------

    def _generate_suffixes(self, word):
        """Yield a couple of indices that indicate a word's suffix"""
        for i in range(len(word)):
            yield [i, len(word)]

    def _to_string(self, element):
        """Return the string that corresponds to the element"""
        return (self._S[element[0] - 1] + "$")[element[1]:element[2]]

    def _check_prefix(self, s1, s2):
        """Check if s1 and s2 have a common prefix and return it's number of characters"""
        for i in range(min(len(s1), len(s2))):
            if s2[i] != s1[i]:
                return i
        return min(len(s1), len(s2))

    def _check_prefix_in_dict(self, dict, word):
        """Check if a suffix in the suffixes array has a common prefix with the word and return the first letter of the
        word and the number of common characters"""
        x = dict.get(word[0])
        if x is not None:
            num = self._check_prefix(word, self._to_string(x._element))
            if num != 0:
                return word[0], num
        return None, None

    def _add_suffix(self, triple_suffix):
        """Add the triple_suffix (suffix consisting of 3 numbers) in the SuffixTree and update all parameters"""
        suffix = self._to_string(triple_suffix)
        root = self._root
        if len(suffix) != 0:
            first_letter, n_chars = self._check_prefix_in_dict(root._children, suffix)
            while first_letter is not None and n_chars == root._children[first_letter]._element[2] - \
                    root._children[first_letter]._element[1]:
                root = root._children[first_letter]
                suffix = suffix[n_chars:]
                triple_suffix[1] += n_chars
                if triple_suffix[0] not in root._mark:
                    root._mark.append(triple_suffix[0])
                if len(suffix) != 0:
                    first_letter, n_chars = self._check_prefix_in_dict(root._children, suffix)
                else:
                    break
            if len(suffix) != 0:
                if first_letter is None:
                    new_node = SuffixTree._Node(triple_suffix, [triple_suffix[0]], root, root._depth + len(suffix) - 1)
                    root._add_child(new_node, suffix[0])
                    self._size += 1
                else:
                    root = root._children[first_letter]
                    triple_suffix[1] += n_chars
                    last_chars = [root._element[0], root._element[1] + n_chars, root._element[2]]
                    suffix = suffix[n_chars:]
                    root._element[2] = root._element[1] + n_chars
                    new_node1 = SuffixTree._Node(last_chars, root._mark[:len(root._mark)], root, root._depth)
                    if len(root._children) == 0:
                        root._depth -= last_chars[2] - last_chars[1] - 1
                    else:
                        root._depth -= last_chars[2] - last_chars[1]
                    if triple_suffix[0] not in root._mark:
                        root._mark.append(triple_suffix[0])
                    for child in root._children.values():
                        child._parent = new_node1
                    new_node1._children = root._children
                    new_node2 = SuffixTree._Node(triple_suffix, [triple_suffix[0]], root, root._depth + len(suffix) - 1)
                    root._children = {self._to_string(last_chars)[0]: new_node1,
                                      self._to_string(triple_suffix)[0]: new_node2}
                    self._size += 2

    def _validate(self, p):
        """Return associated node, if position is valid."""
        if not isinstance(p, self.Position):
            raise TypeError('p must be proper Position type')
        if p._container is not self:
            raise ValueError('p does not belong to this container')
        if p._node._parent is p._node:  # convention for deprecated nodes
            raise ValueError('p is no longer valid')
        return p._node

    def _make_position(self, node):
        """Return Position instance for given node (or None if no node)."""
        return self.Position(self, node) if node is not None else None

    def _common_maximal_substrings(self, c, l):
        """Return the number of common maximal substring"""
        string = self._S[0] + "$"
        n_comm = 0
        prev = -1
        for i in range(len(c) - l + 1):
            node = self._root
            j = i
            while True:
                if j > len(c) - 1:
                    if j > prev and j - i >= l:
                        n_comm += 1
                        prev = j
                    break
                node = node._children.get(c[j])
                if node is None:
                    if j > prev and j - i >= l:
                        n_comm += 1
                        prev = j
                    break
                sub_str = string[node._element[1] + 1:node._element[2]]
                n = 1
                j += 1
                for k in range(len(sub_str)):
                    if j > len(c) - 1:
                        if j > prev and j - i >= l:
                            n_comm += 1
                            prev = j
                        break
                    if c[j] == sub_str[k]:
                        j += 1
                        n += 1
                    else:
                        break
                if (len(node._children) == 0 and n == node._element[2] - node._element[1] - 1) or (
                        len(node._children) != 0 and n == node._element[2] - node._element[1]):
                    if len(node._children) == 0:
                        if j > prev and j - i >= l:
                            n_comm += 1
                            prev = j
                        break
                else:
                    if j > prev and j - i >= l:
                        n_comm += 1
                        prev = j
                    break
        return n_comm

    # ------------------------------- SuffixTree concrete methods for Contest -------------------------------

    def __init__(self, S):
        """Create an initially empty SuffixTree"""
        self._root = self._Node(None, None, None, 0)
        self._size = 1
        self._S = S

        for i in range(len(S)):
            suffixes = self._generate_suffixes(S[i])
            for suffix in suffixes:
                self._add_suffix([i + 1, suffix[0], suffix[1] + 1])

    def getNodeLabel(self, P):
        """Return the substring that labels the node of the SuffixTree to which position P refers
        It throws an exception if P is not valid"""
        node = self._validate(P)
        return self._to_string(node._element)

    def pathString(self, P):
        """Return the substring associated to the path in the SuffixTree from the root to the node to which position P refers
        It throws an exception if P is invalid"""
        path = ""
        node = self._validate(P)

        while node != self._root:
            path = self._to_string(node._element) + path
            node = node._parent

        return path if path[-1] != '$' else path[:-1]

    def getNodeDepth(self, P):
        """Return the length of substring associated to the path in the SuffixTree from the root to the node to which position P refers.
         It throws an exception if P is invalid."""
        return self._validate(P)._depth

    def getNodeMark(self, P):
        """Return the mark of the node of the SuffixTree to which position P refers.
        It throws an exception if P is invalid."""
        return tuple(self._validate(P)._mark)

    def child(self, P, s):
        """Return the position of the child u of the node of SuffixTree to which position P refers such that
            - either s is a prefix of the substring labeling u
            - or the substring labeling u is a prefix of s
        if it exists, and it returns None otherwise (it throws an exception if P is invalid or s is empty)"""
        node = self._validate(P)
        found_node = node._children.get(s[0])
        if found_node is not None:
            str = self._to_string(found_node._element)
            if str[len(str) - 1] == "$":
                str = str[:len(str) - 1]
            if self._check_prefix(s, str) == min(len(s), len(str)):
                return self._make_position(found_node)
        return None
