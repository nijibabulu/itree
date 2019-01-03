# itree

`itree` is an interval tree data structure based on a self-balancing AVL binary search tree tree. 
Suitable for use with sequence features in bioinformatics.

```python
import itree


class MyInterval(object):
    """Any class which implements start and end properties are valid."""
    def __init__(self, start, end):
        self.start = start
        self.end = end  

    def __repr__(self):
        return f"MyInterval(start={self.start},end={self.end})"
        


t = itree.ITree()
t.insert(MyInterval(1,15))
t.insert(MyInterval(3,20))
t.insert(MyInterval(4,20))
t.insert(MyInterval(5,15))
t.insert(MyInterval(6,7))
t.insert(MyInterval(10,20))
t.insert(MyInterval(15,25))

print(t.search(MyInterval(1,4)))
# > [MyInterval(start=3,end=20), MyInterval(start=4,end=20), MyInterval(start=1,end=15)]
```

Insert and search are performed in O(log(n)) operations.