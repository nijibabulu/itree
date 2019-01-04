# itree

`itree` is an interval tree data structure based on a self-balancing AVL binary search tree tree. 
Suitable for use with sequence features in bioinformatics.

## Getting Started

* Construction

Creating an interval tree object:

```python
>>> import itree
>>> t = itree.ITree()
```

* Insertion

Any item inserted into an interval tree must contain "start" and "end" attributes as integers. 

```python
>>> import collections
>>> i = collections.namedtuple('MyInterval', ['start','end'])
>>> t.insert(i(1,15))
>>> t.insert(i(3,20))
>>> t.insert(i(4,20))
>>> t.insert(i(5,15))
>>> t.insert(i(6,7))
>>> t.insert(i(10,20))
>>> t.insert(i(15,25))
```

* Search

Search for all intervals overlapping a given interval

```python 
>>> t.search(i(1,4)) 
[MyInterval(start=3, end=20), MyInterval(start=4, end=20), MyInterval(start=1, end=15)]
```

* Removal

Remove an interval exactly matching the given interval by its `start` and `end` attributes (but not necessarily the 
same object).

```python
>>> t.pstring()
      ┌–(1,15)
–(3,20)
            ┌–(4,20)
      └–(5,15)
            └–(6,7)

>>> t.remove(i(1,15))
>>> t.pstring()
      ┌–(3,20)
            └–(4,20)
–(5,15)
      └–(6,7)
``` 

The `pstring` method is mostly for debugging, but here we illustrate the rebalancing of the tree.
