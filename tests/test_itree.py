import operator
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


simple_tree_pstring = '''\
          ┌–(0,3)
     ┌–(5,8)
          └–(6,10)
–(8,9)
                   ┌–(15,23)
            ┌–(16,21)
     └–(17,19)
                   ┌–(19,20)
            └–(25,30)
                   └–(26,27)
'''

@pytest.mark.itree
def test_tree_pstring(itree_simple_sample):
    tree = itree.ITree(nodes=itree_simple_sample)

    assert tree.pstring() == simple_tree_pstring


@pytest.mark.itree
def test_node_str(itree_simple_sample):
    node = itree.ITreeNode(itree_simple_sample[0])

    assert str(node) == f'({node.start},{node.end})'


@pytest.mark.itree
def test_node_pstring(itree_simple_sample):
    node = itree.ITreeNode(itree_simple_sample[0])
    pstring = node.pstring(name=True, attr_names=True, minmax=True, height=True)
    expected = f"ITreeNode(start={node.start},end={node.end},"\
               f"min={node.start},max={node.end},height=1)"

    assert pstring == expected


@pytest.mark.itree
def test_node_str(itree_simple_sample):
    tree = itree.ITree(nodes=itree_simple_sample)
    expected = f"ITree(root=({tree.root.start},{tree.root.end}))"

    assert str(tree) == expected


@pytest.mark.itree
def test_remove_nothing(FakeITree, FakeNode, itree_simple_sample):
    tree = itree.ITree(nodes=itree_simple_sample)
    nonpresent_node = FakeNode(100000,200000)
    assert nonpresent_node not in itree_simple_sample, \
        f"{nonpresent_node} is in the sample; revise the test"
    expected = FakeITree(itree_simple_sample)
    tree.remove(nonpresent_node)

    test_node = itree_simple_sample[0]

    assert len(tree) == len(expected)
    assert tree.search(test_node) == expected.search(test_node)


@pytest.mark.itree
def test_search_empty_tree(FakeITree, FakeNode):
    tree = itree.ITree()
    test_node = FakeNode(3,15)

    assert tree.search(test_node) == []


@pytest.mark.grouped_itree
def test_create_grouped_itree(gene_intervals_short):
    tree = itree.GroupedITree(key=lambda node: node.annotation,
                              intervals=gene_intervals_short)

    assert tree is not None


@pytest.mark.grouped_itree
def test_grouped_itree_too_long_key_signature():
    with pytest.raises(TypeError):
        itree.GroupedITree(key=lambda a,b,c: None)


@pytest.mark.grouped_itree
def test_grouped_itree_too_short_key_signature():
    with pytest.raises(TypeError):
        itree.GroupedITree(key=lambda: None)


@pytest.mark.grouped_itree
def test_grouped_itree_non_string_non_callable_key():
    with pytest.raises(TypeError):
        itree.GroupedITree(key=1)


@pytest.mark.grouped_itree
def test_create_grouped_itree(gene_intervals_short):
    tree = itree.GroupedITree(key='annotation',
                              intervals=gene_intervals_short)

    assert tree is not None

    expected = "GroupedITree(key=annotation, trees={'Chr10': ITree(root=(613874,621867))})"

    assert str(tree) == expected


@pytest.mark.grouped_itree
def test_insert_grouped_itree(FakeGroupedITree, gene_intervals_short):
    tree = itree.GroupedITree(key="annotation")
    fake_tree = FakeGroupedITree(key="annotation",
                                 intervals=gene_intervals_short)
    for node in gene_intervals_short:
        tree.insert(node)

    assert tree.search(gene_intervals_short[0]) == \
        fake_tree.search(gene_intervals_short[0])


@pytest.mark.grouped_itree
def test_remove_grouped_itree(FakeGroupedITree, gene_intervals_short):
    tree = itree.GroupedITree(key="annotation",
                              intervals=gene_intervals_short)
    fake_tree = FakeGroupedITree(key="annotation",
                                 intervals=gene_intervals_short)

    tree.remove(gene_intervals_short[0])
    fake_tree.remove(gene_intervals_short[0])

    assert tree.search(gene_intervals_short[0]) == \
           fake_tree.search(gene_intervals_short[0])

@pytest.mark.grouped_itree
def test_search_grouped_itree_string(FakeGroupedITree, gene_intervals_short):
    tree = itree.GroupedITree(key=lambda node: node.annotation,
                              intervals=gene_intervals_short)

    assert tree is not None

    fake_tree = FakeGroupedITree(key=lambda node: node.annotation,
                                 intervals=gene_intervals_short)

    assert tree.search(gene_intervals_short[0]) == \
           fake_tree.search(gene_intervals_short[0])


@pytest.mark.grouped_itree
def test_search_grouped_itree_callable(FakeGroupedITree, gene_intervals_short):
    tree = itree.GroupedITree(key='annotation',
                              intervals=gene_intervals_short)

    assert tree is not None


@pytest.mark.grouped_itree
def test_search_grouped_itree_nonexistent_key(FakeNode, gene_intervals_short):
    tree = itree.GroupedITree(key='annotation', intervals=gene_intervals_short)
    assert tree is not None

    assert tree.search(FakeNode(1,2,annotation='IAMNOTANANNOTATION')) == []





