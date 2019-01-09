import os
import abc
import collections
import random
import re
import sys

import itertools
import timeit
from typing import Callable, List, Tuple, TypeVar, Generic, NewType, Set, \
    Iterable, Optional, TextIO

import intervaltree
import click

import itree

T = TypeVar('T')
S = TypeVar('S')
IV = NewType('IV', Tuple[int, int])


class IntervalContainerProxy(Generic[T, S]):
    """define methods required for an interval container adapter, to
    facilitate the benchmarking of the container itself via `timeit`. Some
    methods return closures to enable the reuse of the data within the code."""

    __meta__ = abc.ABCMeta

    def __init__(self, intervals: List[S]):
        self._construct = self.constructor(self.encode_intervals(intervals))
        self._object = None

    @property
    def construct(self):
        """Method to construct a new

        :return: a new interval container object populated with intervals
        """
        return self._construct

    @property
    def object(self):
        """The current object after performing the last operation, if one
        has been performed."""
        return self._object

    @property
    def methname(self):
        return re.sub(r"Proxy$", '', self.__class__.__name__).lower()

    @classmethod
    def encode_intervals(cls, intervals: Iterable[IV]) -> List[S]:
        """encode list of tuple pairs of ints into native interval types """
        ...

    @classmethod
    def decode_intervals(cls, intervals: Iterable[S]) -> List[IV]:
        """encode list of tuple pairs of ints into native interval types """
        ...

    @classmethod
    def contents(cls, t: T) -> Set[IV]:
        """return the contents of the tree"""
        ...

    def constructor(self, intervals: S) -> Callable[[], T]:
        """return a function that constructs an interval container with
        intervals"""
        ...

    def searcher(self, intervals: S) -> Callable[[], List[S]]:
        """return searching code. no database is given. persistence must
        be handled via the construct method."""
        ...

    def remover(self, intervals: S) -> Callable[[], None]:
        """return removing code. no database is given. persistence must
        be handled via the construct method invoked from this method."""
        ...


NamedIV = collections.namedtuple('MyInterval', ['start', 'end'])


class ITreeProxy(IntervalContainerProxy):
    """A proxy for the `itree` interval tree implementation."""

    @classmethod
    def encode_intervals(cls, intervals):
        return [NamedIV(*iv) for iv in intervals]

    @classmethod
    def decode_intervals(cls, intervals: List[NamedIV]) -> List[IV]:
        return [tuple(iv) for iv in intervals]

    @classmethod
    def contents(cls, t: T):
        """currently not implemented in itree."""
        s = [t.root]
        result = set()
        while len(s):
            n = s.pop()
            children = [c for c in n.c if c is not None]
            result.update(children)
            s += children
        return result

    def constructor(self, intervals) -> Callable[[], itree.ITree]:
        self._object = itree.ITree(intervals)
        return lambda: itree.ITree(intervals)

    def searcher(self, intervals) -> Callable[[], List[NamedIV]]:
        self._object = self.construct()
        return lambda: list(itertools.chain.from_iterable(
            [self.object.search(i) for i in intervals]))

    def remover(self, intervals) -> Callable[[], List[NamedIV]]:
        self._object = self.construct()
        return lambda: [self._object.remove(i) for i in intervals]


class IntervalTreeProxy(IntervalContainerProxy):
    """A proxy for the `intervaltree` interval tree implementation"""

    @classmethod
    def encode_intervals(cls, intervals):
        return [intervaltree.Interval(*iv) for iv in intervals]

    @classmethod
    def decode_intervals(cls, intervals: Iterable[S]) -> List[IV]:
        return [(int(iv.begin), int(iv.end)) for iv in intervals]

    @classmethod
    def contents(cls, t: intervaltree.IntervalTree):
        return set((int(iv.begin), int(iv.end)) for iv in t.all_intervals)

    def constructor(self, intervals):
        self._object = intervaltree.IntervalTree(intervals=intervals)
        return lambda: intervaltree.IntervalTree(intervals=intervals)

    def searcher(self, intervals):
        self._object = self.construct()
        return lambda: list(itertools.chain.from_iterable(
            [self._object.overlap(i) for i in intervals]))

    def remover(self, intervals):
        self._object = self.construct()
        return lambda: [self._object.discard(i) for i in intervals]


class NaiveProxy(IntervalContainerProxy):
    """A proxy for the unordered list solution of storing and searching for
    intervals"""

    @classmethod
    def encode_intervals(cls, intervals):
        return intervals

    @classmethod
    def decode_intervals(cls, intervals: List[IV]) -> List[IV]:
        return intervals

    @classmethod
    def contents(cls, t: List[IV]):
        return set(t)

    def constructor(self, intervals):
        self._object = [iv for iv in intervals]
        return lambda: [iv for iv in intervals]

    def searcher(self, intervals):
        self._object = self.construct()
        return lambda: list(itertools.chain.from_iterable(
            [[dbi for dbi in self._object if i[0] <= dbi[1] and dbi[0] <= i[1]]
             for i in intervals]
        ))

    def remover(self, intervals):
        self._object = self.construct()
        return lambda: [dbi for dbi in self._object if dbi not in intervals]


class Benchmarker(Generic[T, S]):
    """A class to benchmark the an interval tree implementation."""

    def __init__(self, proxy: IntervalContainerProxy[T, S],
                 validator_proxy: Optional[IntervalContainerProxy[T, S]] = None,
                 validator_stream: TextIO = sys.stderr,
                 repeat: int = 12):
        """Construct a benchmarker

        :param proxy: Any concrete IntervalTreeProxy class.
        :param validator_proxy: A proxy against which to validate the results
            prior to benchmarking.
        :param repeat: The number of times to repeat each benchmark operation.
        """
        self.proxy = proxy
        self.validator = validator_proxy
        self.validator_stream = validator_stream
        self.repeat = repeat

    def search(self, intervals: List[IV]) -> Set[IV]:
        """Perform the search once, untimed for verification purposes

        :param intervals: a list of intervals to search for
        :return: a set of intervals found by the method
        """
        result = self.proxy.searcher(self.proxy.encode_intervals(intervals))()
        return set(self.proxy.decode_intervals(result))

    def validate_sets(self, label, acquired, expected):
        if expected == acquired:
            self.validator_stream.write(f'{self.proxy.methname} {label} '
                                        f'valid ({len(expected)} expected)\n')
        else:
            self.validator_stream.write(
                f'{self.proxy.methname} {label} not validated. '
                f'{len(expected - acquired)} additional intervals and '
                f'{len(acquired - expected)} missing intervals found.\n')

    def validate_state(self, label, acquired, expected):
        self.validate_sets(label,
                           self.proxy.contents(self.proxy.object),
                           self.proxy.contents(self.proxy.object))

    def validate_results(self, label, acquired, expected):
        self.validate_sets(label,
                           set(self.proxy.decode_intervals(acquired)),
                           set(self.validator.decode_intervals(expected)))

    def validate(self, label, intervals, method, validate_method, comparer):
        result = method(self.proxy.encode_intervals(intervals))()
        validate_result = validate_method(
            self.validator.encode_intervals(intervals))()
        comparer(label, result, validate_result)

    def do_bench(self, intervals, method) -> List[float]:
        prepped_intervals = self.proxy.encode_intervals(intervals)
        return [timeit.timeit(method(prepped_intervals), number=1)
                for _ in range(self.repeat)]

    def bench(self, insert_intervals: List[IV],
              search_intervals: List[IV],
              remove_intervals: List[IV]
              ) -> Tuple[List[float], List[float], List[float]]:
        """Perform a benchmarking test of the three operations in order:
        construction and intialization (from the `insert_intervals`),
        removal and searching.

        :param insert_intervals: intervals to insert
        :param search_intervals: intervals to search for
        :param remove_intervals: intervals to remove
        :return: a tuple of lists of run times for each of the operations
            insert, remove and search in that order.
        """
        if self.validator:
            self.validate(
                label=f"insert {len(insert_intervals)}",
                intervals=insert_intervals,
                method=self.proxy.constructor,
                validate_method=self.validator.constructor,
                comparer=self.validate_state)
            self.validate(
                label=f"remove {len(insert_intervals)} {len(remove_intervals)}",
                intervals=remove_intervals,
                method=self.proxy.remover,
                validate_method=self.validator.remover,
                comparer=self.validate_state)
            self.validate(
                label=f"search {len(insert_intervals)} {len(search_intervals)}",
                intervals=search_intervals,
                method=self.proxy.searcher,
                validate_method=self.validator.searcher,
                comparer=self.validate_results)

        return self.do_bench(insert_intervals, self.proxy.constructor), \
               self.do_bench(remove_intervals, self.proxy.remover), \
               self.do_bench(search_intervals, self.proxy.searcher)


def do_bench(proxy_cls, validator_cls, insert_intervals, search_intervals,
             remove_intervals, repeat=12):
    proxy = proxy_cls(insert_intervals)
    validator = validator_cls(insert_intervals)
    b = Benchmarker(proxy=proxy, validator_proxy=validator, repeat=repeat)

    result = b.bench(insert_intervals, search_intervals, remove_intervals)
    tree_size = len(insert_intervals)
    for op, subset, rs in zip(['insert', 'remove', 'search'],
                              [insert_intervals, search_intervals,
                               remove_intervals],
                              result):
        size = len(subset)
        print('\n'.join('\t'.join(
            str(x) for x in [b.proxy.methname, tree_size, size, op, r]
        ) for r in rs))


@click.command()
@click.option('--search-frac', type=float, show_default=True, default=.5,
              help="Sample this fraction of intervals for benchmarking search")
@click.option('--remove-frac', type=float, show_default=True, default=.5,
              help="Sample this fraction of intervals benchmarking remove")
@click.option('--seed', type=int, show_default=True, default=121080)
@click.argument('BED_FILE')
@click.argument('MIN_TREE_SIZE', type=int)
@click.argument('MAX_TREE_SIZE', type=int)
@click.argument('STEP_SIZE', type=int)
def main(seed, bed_file, search_frac, remove_frac, min_tree_size, max_tree_size,
         step_size):
    random.seed(seed)

    with open(bed_file) as f:
        ivs = [tuple(int(x) for x in l.split()[1:3]) for l in f]

    for s in range(min_tree_size, max_tree_size, step_size):
        insert_ivs = random.sample(ivs, s)
        search_ivs = random.sample(insert_ivs, int(s * search_frac))
        remove_ivs = random.sample(insert_ivs, int(s * remove_frac))

        for proxy in [ITreeProxy, IntervalTreeProxy, NaiveProxy]:
            do_bench(proxy, NaiveProxy, insert_ivs, search_ivs, remove_ivs)


if __name__ == '__main__':
    main()
