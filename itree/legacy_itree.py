"""
This is an older, slower version of the intervaltree implementation that
was previously used. Kept in the repository for testing
"""


class ITreeNode(object):
    def __init__(self, i):
        self.i = i
        self._init_coords(i.start, i.end)

    def _init_coords(self, start, end):
        self.start = start
        self.end = end
        self.max = end
        self.left = None
        self.right = None

    @classmethod
    def from_coords(cls, start, end):
        obj = cls.__new__(cls)
        obj._init_coords(start, end)
        return obj


class ITree(object):
    def __init__(self, nodes=None):
        self.root = None
        if nodes is not None:
            # approximate a balanced tree by adding nodes
            # in order of closeness to the center.
            center = max(n.start for n in nodes) / 2
            for n in sorted(nodes, key=lambda n: abs(n.start - center)):
                self.insert(n)

    def insert(self, i):
        n = ITreeNode(i)
        if self.root is None:
            self.root = n
            return
        ncur = self.root
        while True:
            ncur.max = max(i.end, ncur.max)
            if i.start < ncur.start:
                if ncur.left is None:
                    ncur.left = n
                    break
                else:
                    ncur = ncur.left
            else:
                if ncur.right is None:
                    ncur.right = n
                    break
                else:
                    ncur = ncur.right

    def search(self, i):
        result = []
        if self.root is None:
            return result
        nstack = [self.root]
        while len(nstack):
            ncur = nstack.pop()
            if ncur.start <= i.end and i.start <= ncur.end:
                result.append(ncur.i)
            if ncur.left is not None and ncur.left.max >= i.start:
                nstack.append(ncur.left)
            if ncur.right is not None:
                nstack.append(ncur.right)
        return result
