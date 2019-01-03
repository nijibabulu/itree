from . import itree
from . import legacy_itree

ITree = itree.ITree
ITreeNode = itree.ITreeNode
GroupedITree = itree.GroupedITree


def use_legacy_itree():
    global ITree, ITreeNode
    ITree = legacy_itree.ITree
    ITreeNode = legacy_itree.ITreeNode


__version__ = '0.0.1'
