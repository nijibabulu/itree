import random
import sys

import pytest
import itree


@pytest.mark.itree
def test_insert(itree_simple_sample):
    t = itree.ITree()
    for node in itree_simple_sample:
        t.insert(node)


@pytest.mark.itree
def test_complex_insert(itree_complex_sample):
    t = itree.ITree()
    for node in itree_complex_sample:
        t.insert(node)


@pytest.mark.itree
def test_random_insert(FakeNode, itree_random_intervals):
    t = itree.ITree()
    for node in itree_random_intervals:
        t.insert(node)


@pytest.mark.itree
def test_random_remove(itree_random_intervals):
    t = itree.ITree()
    for node in itree_random_intervals:
        t.insert(node)

    for node in itree_random_intervals[::5]:
        old_size = len(t)
        t.remove(node)
        new_size = len(t)
        assert new_size == old_size-1


@pytest.mark.itree
def test_remove_all_nodes(itree_random_intervals):
    t = itree.ITree()
    nodes = list(sorted(list(set(itree_random_intervals))))

    for node in nodes:
        t.insert(node)

    for node in nodes:
        old_size = len(t)
        t.remove(node)
        new_size = len(t)
        assert new_size == old_size-1

    assert len(t) == 0


@pytest.mark.itree
def test_node_really_removed(itree_complex_sample):
    t = itree.ITree()
    nodes = list(sorted(list(set(itree_complex_sample))))

    for node in nodes:
        t.insert(node)

    for node in nodes[::5]:
        t.remove(node)
        for r in t.search(node):
            assert f"({r.start},{r.end})" != f"({node.start},{node.end})"


@pytest.mark.itree
@pytest.mark.parametrize("seed", range(2))
def test_search(FakeITree, itree_random_intervals, itree_random_queries, seed):
    random.seed(random.randint(0, sys.maxsize))
    tree = itree.ITree(nodes=itree_random_intervals)
    mock_tree = FakeITree(nodes=itree_random_intervals)
    for search in itree_random_queries:
        if len(mock_tree.search(search)) != len(tree.search(search)):
            tree.search(search)
            print(f"seed == {seed}")
            assert len(mock_tree.search(search)) == len(tree.search(search))


@pytest.mark.itree_long
def test_genes(FakeITree, gene_intervals):
    tree = itree.ITree(nodes=gene_intervals)
    mock_tree = FakeITree(nodes=gene_intervals)
    for search in gene_intervals:
        if len(mock_tree.search(search)) != len(tree.search(search)):
            tree.search(search)
            assert len(mock_tree.search(search)) == len(tree.search(search))
