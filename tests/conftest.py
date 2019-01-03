import random

import pytest
import attr


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runlong"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runlong option to run")
    for item in items:
        if any("long" in k for k in item.keywords):
            item.add_marker(skip_slow)


def pytest_addoption(parser):
    parser.addoption(
        "--runlong", action="store_true", default=False, help="run full tests"
    )


samp = [(1, 1040), (1, 1883), (1, 835), (517, 18575), (517, 36465),
        (517, 52279), (517, 52279), (517, 52279), (517, 52279), (517, 52279),
        (2934, 5665), (6076, 8444), (10354, 16765), (16930, 18685),
        (19477, 20605), (25547, 36465), (25926, 30914), (33284, 36965),
        (37292, 44515), (37734, 52279), (37734, 52279), (37734, 52279),
        (37734, 52279), (37734, 52279), (38893, 52279), (44587, 46135),
        (46266, 52545), (55017, 56405), (55017, 63985), (57276, 63498),
        (66516, 76026), (66516, 81362), (66516, 85542), (66516, 88500),
        (72856, 78620), (72856, 81877), (78627, 81915), (81576, 85380),
        (85941, 86873), (85942, 88965), (85942, 88965), (88027, 88965),
        (89716, 94537), (89716, 94537), (91316, 111640), (91316, 94537),
        (91316, 94705), (94904, 95275), (96286, 98570), (96376, 98570),
        (98577, 103515), (98577, 103515), (98577, 104895), (101827, 102505),
        (101827, 103395), (101827, 103515), (101827, 104125), (103776, 104840),
        (103776, 107150), (103776, 108999), (104857, 105325), (104857, 105955),
        (104857, 106365), (106476, 109877), (106986, 107770), (106986, 111640),
        (107177, 107695), (107796, 108999), (110146, 113226), (110928, 111815),
        (111876, 113007), (112298, 113007), (114066, 114745), (114066, 114885),
        (114066, 115135), (114066, 115677), (116465, 121885), (116465, 123463),
        (116465, 123463), (122937, 123463), (125324, 127355), (125324, 139310),
        (125324, 142421), (125324, 142421), (125324, 142421), (125324, 142421),
        (126896, 127355), (130616, 142720), (139796, 142421), (143368, 144545),
        (144863, 145655), (144863, 156882), (144863, 156882), (158697, 165901),
        (167127, 169145), (167127, 169145), (171779, 175720), (171779, 190559),
        (171779, 190559), (171779, 215826)]


@attr.s(frozen=True)
class _FakeNode(object):
    start: int = attr.ib()
    end: int = attr.ib()


@pytest.fixture
def FakeNode():
    return _FakeNode


@pytest.fixture
def itree_complex_sample():
    return [_FakeNode(*t) for t in samp]


@pytest.fixture
def itree_simple_sample():
    return [_FakeNode(*t) for t in [(0, 3), (6, 10), (5, 8), (8, 9), (15, 23),
                                    (16, 21), (25, 30), (17, 19), (26, 27),
                                    (19, 20)]]


def random_intervals(n, max, width):
    samples = []
    for i in range(n):
        start = random.randint(0, max)
        end = random.randint(start, start + width)
        samples.append(_FakeNode(start, end))
    return samples


@pytest.fixture
def itree_random_intervals():
    return random_intervals(n=1000, max=20000, width=1000)


@pytest.fixture
def itree_random_queries():
    return random_intervals(n=100, max=20000, width=1000)


@pytest.fixture
def gene_intervals():
    f = open('genes.mcl1.bed')
    nodes = []
    for line in f:
        start, end = [int(x) for x in line.split('\t')[1:3]]
        nodes.append(_FakeNode(start, end))
    return nodes


class _FakeITree(object):
    def __init__(self, nodes=None):
        self.nodes = nodes or []

    def insert(self, node):
        self.nodes.append(node)

    def search(self, i):
        return [n for n in self.nodes if n.start <= i.end and i.start <= n.end]


@pytest.fixture
def FakeITree():
    return _FakeITree
