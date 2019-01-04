"""
Interval tree implementation suitable for gene objects.
"""
import sys
import inspect
import itertools
from typing import List, Optional

"""

This is a special case of the AVL balanced binary search tree in which we keep
track of the maximum and minimum value of each subtree during insertions in
order to avoid excessively long searches. The usual implementation only tracks
the maximum value of the subtree. This is suitable when searching for a single
unique interval, but not when searching for all overlapping intervals. For
example:

                                |(16,21)|
                                |  0-20 |
                            /              \
                   |(8,9)|                    |(25,30)|
                   | 0-23|                    | 20-26 |
                  /       \                  /         \
          |(5,8)|          |(15,23)||(17,19)|           |(26,26)|
          | 0-10|          | 15-23 || 17-20 |           | 26-26 |

In the above example, if we were searching for an interval overlapping (16, 20),
a standard interval tree implementation, which usually only stores the maximum
value of the subtree, would search the left subtree only and return (15,23).
However, we may also be interested in (17,19). Using only the maximum subtree
would require us to alwasy search the right subtree. Storing both the maximum
and the minimum prevents us from, in this example, exploring the rightmost
leaf.
"""


class ITreeNode(object):
    """Internal wrapper object for an interval tree node.

    In most cases, there would be no need to use this class directly. Any
    interval object with the properties ``start`` and ``end`` can be used.
    Interval trees wrap interval objects in the ``ITreeNode`` class and
    return the original matching object.
    """

    def __init__(self, i):
        """Initialize a an ITreeNode object.

        :param i: An interval object with ``start`` and ``end``
            properties/attributes.
        """
        self.interval = i
        self.min: int = min(i.start, i.end)
        self.max: int = max(i.end, i.start)
        self.c: List[ITreeNode] = [None, None]
        self.height: int = 1

    @property
    def interval(self):
        """the contained interval object"""
        return self.i

    @interval.setter
    def interval(self, i):
        self.i = i
        self.start = i.start
        self.end = i.end

    @property
    def left(self):
        """The left child of the node

        The left child start is less than or equal to the node's start"""
        return self.c[0]

    @left.setter
    def left(self, n):
        self.c[0] = n

    @property
    def right(self):
        """The right child of the node

        The right child start is greater than or equal to the node's start"""
        return self.c[1]

    @right.setter
    def right(self, n):
        self.c[1] = n

    def __repr__(self):
        return self.pstring()
        # return f"ITreeNode({self.start},{self.end})"  # ,max={self.max}," \
        # f"height={self.height})"

    def pstring(self, name=False, attr_names=False, minmax=False, height=False):
        """pretty string of the node

        :param name: show the name of the class (i.e. ITreeNode)
        :param attr_names: show the names of the attrs (e.g. start=S,end=E)
        :param minmax: show the min and max of the name
        :param height: show the height of the node
        :return: a string
        """

        s = ""
        if name:
            s += "ITreeNode"
        s += "("
        attrs = ["start", "end"] + \
                (["min", "max"] if minmax else []) + \
                (["height"] if height else [])
        s += ','.join(
            f"{(attr + '=') if attr_names else ''}{getattr(self,attr)}"
            for attr in attrs)
        s += ")"

        return s


class ITree(object):
    """Self-balancing interval for fast queries of arbitrary interval objects.

    Objects are wrapped in an internal structure and may be of any time as long
    as they have integer ``start`` and ``end`` properties or attributes.
    Queries via ``search`` need not be the same object, but have the same
    requirements.
    """

    def __init__(self, nodes=None):
        """Initialize an interval tree, optionally with interval objects."""
        self.root = None
        if nodes is not None:
            for n in nodes:
                self.insert(n)

    def __len__(self):
        return self._child_count(self.root)

    def __repr__(self):
        return f"ITree(root={self.root})"

    def pstring(self, name=False, attr_names=False, minmax=False, height=False):
        """pretty string of the tree

        Display the binary tree in order including additional information if
        requested.

        :param name: show the name of the class (i.e. ITreeNode)
        :param attr_names: show the names of the attrs (e.g. start=S,end=E)
        :param minmax: show the min and max of the name
        :param height: show the height of the node
        :return: a string"""
        return self._in_order(self.root, name=name, attr_names=attr_names,
                              minmax=minmax, height=height)

    def _in_order(self, n, right_parent=False, level=0, **kwargs):

        if n is None:
            return ""
        if level:
            corner = '└' if right_parent else '┌'
        else:
            corner = ''

        node_string = n.pstring(**kwargs)
        left_subtree_string = self._in_order(
            n.left, right_parent=False, level=level + len(node_string), **kwargs)
        right_subtree_string = self._in_order(
            n.right, right_parent=True, level=level + len(node_string), **kwargs)

        return f"{left_subtree_string}{(' '*level)+corner}–{node_string}\n{right_subtree_string}"

    def _child_count(self, n):
        if n is None:
            return 0
        return 1 + self._child_count(n.left) + self._child_count(n.right)

    @staticmethod
    def _height(n):
        return n.height if n is not None else 0

    @staticmethod
    def _max(n):
        return n.max if n is not None else 0

    @staticmethod
    def _min(n):
        return n.min if n is not None else sys.maxsize

    def _rotate(self, n: ITreeNode, heavy: bool) -> ITreeNode:
        # Rotate a tree to balance it. This generalizes the left and right
        # rotate operations by denoting "heavy" as the side which will
        # child n which will become root. (False=left, True=right).
        # The operation is as follows, with the right rotate operation
        # represented by the variables:
        #         n                                 r
        #       /   \                             /   \
        #     r               ----> right              n
        #   /   \             left <-----            /   \
        #         t                                t
        light = not heavy

        # save the nodes that will be exchanged (r=new root, t=moved subtree)
        r = n.c[heavy]
        t = r.c[light]

        # exchange the children
        r.c[light] = n
        n.c[heavy] = t

        # update the heights for future balancing operations. In most cases
        # it will be unknown if the child is None, hence the helper functions.
        n.height = 1 + max(self._height(n.c[light]), self._height(n.c[heavy]))
        r.height = 1 + max(r.c[light].height, self._height(r.c[heavy]))

        # Update the mins and maxes of the nodes.
        n.max = max(self._max(n.c[light]), self._max(n.c[heavy]), n.end)
        r.max = max(r.c[light].max, self._max(r.c[heavy]), r.end)

        n.min = min(self._min(n.c[light]), self._min(n.c[heavy]), n.start)
        r.min = min(r.c[light].min, self._min(r.c[heavy]), r.start)

        return r

    def insert(self, i):
        """Insert an interval into the tree.

        The object is wrapped in an internal structure and need only have
        a ``start`` and ``end`` attribute or property.
        """
        self.root = self._insert(self.root, ITreeNode(i))

    def _insert(self, n: ITreeNode, nn: ITreeNode) -> ITreeNode:
        if n is None:
            return nn

        # set the upper limit
        n.max = max(nn.end, n.max)
        n.min = min(nn.start, n.min)

        # insert the to either the right or left subtree
        if nn.start < n.start:
            n.left = self._insert(n.left, nn)
        else:
            n.right = self._insert(n.right, nn)

        return self._rebalance(n)

    def _rebalance(self, n: ITreeNode) -> ITreeNode:
        # rebalance a tree

        # check for balancing: first get the height of the current node
        # via its children. we assume the children balance is already correct
        balance = self._balance(n, update_node_height=True)

        # re-balance the nodes where needed. If the tree is left heavy, then
        # rotate to the right. An insert or delete led to a a second
        # imbalance (e.g. a node was inserted to a right grandchild).
        # In these cases we rotate twice.
        if balance > 1:
            if self._balance(n.left) < 0:
                n.left = self._rotate(n.left, True)
            return self._rotate(n, False)
        elif balance < -1:
            if self._balance(n.right) > 0:
                n.right = self._rotate(n.right, False)
            return self._rotate(n, True)
        else:
            return n

    def _balance(self, n: ITreeNode, update_node_height: bool = False):
        left_height = self._height(n.left)
        right_height = self._height(n.right)
        if update_node_height:
            n.height = 1 + max(left_height, right_height)

        # check the balance
        return left_height - right_height

    def remove(self, i):
        """Remove an interval from a tree

        The object must be present in the tree (identical start and stop).
        """
        self.root = self._remove(self.root, None, False, ITreeNode(i))

    def _remove(self, n: ITreeNode, p: Optional[ITreeNode],
                right_parent: bool, nn: ITreeNode) -> Optional[ITreeNode]:
        """Removal helper function """

        if n is None:
            return None
        # BST removal consists of 3 cases:
        # 1 if the node has 2 children, the node is replaced with the value
        #   of its smallest right child (the leftmost child with no left child),
        #   and the node containing that value is removed.
        # 2 if the node has 1 child, the parent link to the node to be removed
        #   then points to the nodes only child
        # 3 if the node has no children the node is simply removed.

        # case 1 implies that case 2 or 3 will be performed on a child node,
        # so long as it is found. successive updates to the nodes will be
        # propagated up after the child removal

        if nn.start == n.start and nn.end == n.end:
            if n.left is not None and n.right is not None:
                min_right_child = self._min_child(n.right)
                n.interval = min_right_child.interval
                n.right = self._remove(n.right, n, True, min_right_child)
            else:
                # less than two children, we bridge the parent to the child
                n = n.left or n.right
                if p is not None:
                    p.c[right_parent] = n
                if n is None:
                    return None
        else:
            if n.left and nn.start <= n.left.max and n.left.min <= nn.end:
                n.left = self._remove(n.left, n, False, nn)
            if n.right and nn.start <= n.right.max and n.right.min <= nn.end:
                n.right = self._remove(n.right, n, True, nn)

        n.min = min(self._min(n.left), self._min(n.right), n.start)
        n.max = max(self._max(n.left), self._max(n.right), n.end)

        return self._rebalance(n)

    def _min_child(self, n: ITreeNode):
        if n.left is None:
            return n
        else:
            return self._min_child(n.left)

    def search(self, i):
        """Return all overlapping instances of a given interval.

        The interval need not be of the same class but is required to have
        a ``start`` and ``end`` attribute or parameter.
        """

        # We use a non-recursive implementation since recursion is expensive
        result = []
        if self.root is None:
            return result

        # Add the first node
        stack = [self.root]
        while len(stack):
            n = stack.pop()

            # Add the object to the result if it overlaps
            if n.start <= i.end and i.start <= n.end:
                result.append(n.i)

            # Explore subtrees that overlap with the interval
            if n.left and i.start <= n.left.max and n.left.min <= i.end:
                stack.append(n.left)
            if n.right and i.start <= n.right.max and n.right.min <= i.end:
                stack.append(n.right)

        return result


class GroupedITree(object):
    def __init__(self, key, nodes=None):
        """A collection of ITree objects partitioned by a key value

        :param key: either a string indicating the name of the attribute
            or a function to group the objects by
        :param nodes: an optional list of objects to initialize the ITrees with
        """

        if isinstance(key, str):
            self.key = lambda g: getattr(g, key)
        elif callable(key):
            sig = inspect.signature(key)
            if len(sig.parameters) != 1:
                raise TypeError("key must be a function which accepts a single "
                                "object.")
            self.key = key
        else:
            raise TypeError("key must be a string or a callable.")

        self.trees = {}
        if nodes is not None:
            self.trees = {
                k: ITree(nodes=list(grp))
                for k, grp in itertools.groupby(
                sorted(nodes, key=self.key), key=self.key)
            }

    def insert(self, i):
        self.trees.setdefault(self.key(i), ITree()).insert(i)

    def search(self, i):
        k = self.key(i)
        if k not in self.trees:
            return []
        else:
            return self.trees[k].search(i)
