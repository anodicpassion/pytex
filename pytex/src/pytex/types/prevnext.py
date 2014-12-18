'''This module contains auxiliary types that are not TeXElements but are
used internally in their implementation.'''

import copy as _copy
import sys as _sys

#===============================================================================
# Linked elements
#===============================================================================
class Element:
    '''An element that have an prev/next relationship with other Elements.
    
    Note on implementation: the information about the prev/next relationships
    is stored into a MasterList object external to the Element. This object
    guarantees a consistent relation among a group of Elements and also offer
    a list-like interface to access those elements.
    
    Master lists can be created separately or implicitly as in the example usage
    bellow:
    
    >>> class pnstr(str, Element): pass
    >>> a = pnstr('a')
    >>> a.insert_next(pnstr('b'))
    >>> a.get_siblings()
    ['a', 'b']
    
    >>> a.get_siblings_next()
    ['b']
    >>> a.get_siblings_prev()
    []
    
    Deepcopy operations return unlinked objects
    
    >>> import copy
    >>> A = copy.deepcopy(a); A.get_siblings()
    ['a']
    
    Elements do not define a __init__() method, hence it does not need to be
    called expliclty by subclasses.
    '''
    # TODO: reimplement the reference system to remove the _masterlist attribute
    # so we can define __slots__ on subtypes
    #
    # If we had defined __slots__ = ('masterlist') here, it would be impossible
    # to have multiple inheritance with C-types such as str, list, etc.

    _masterlist = None

    def _set_masterlist(self, mlist):
        mlist_old = self._masterlist
        if mlist_old is not None and mlist_old is not mlist:
            raise ValueError('%r already in a Masterlist' % self)
        else:
            self._masterlist = mlist

    def __getstate__(self):
        state = dict(self.__dict__)
        state.pop('_masterlist', None)
        return state

    def unlink(self):
        '''Remove itself from list.'''

        if self._masterlist is not None:
            self._masterlist.pop(self.idx)

    def unlinked(self):
        '''Remove iteself from list and return'''

        self.unlink()
        return self

    def copy_unlinked(self, deepcopy=True):
        '''Return a copy of itself'''

        try:
            ml = self.__dict__.pop('_masterlist', None)
            if deepcopy:
                cp = _copy.deepcopy(self)
            else:
                cp = _copy.copy(self)
        finally:
            self._masterlist = ml
        return cp

    def replace_by(self, other):
        '''Replace itself by the other object. 
        
        The object will be unlinked from the list.'''

        if self._masterlist is not None:
            self._masterlist[self.idx] = other
        else:
            raise ValueError('object is not linked')

    def insert_next(self, obj):
        '''Insert obj in the lists of objects just after itself'''

        if self._masterlist is not None:
            self._masterlist.insert(self.idx + 1, obj)
        else:
            self._masterlist = Masterlist([obj])
            self._masterlist.insert(0, self)

    def insert_prev(self, obj):
        '''Insert the given object prior to itself'''

        if self._masterlist is not None:
            self._masterlist.insert(self.idx, obj)
        else:
            self._masterlist = Masterlist([obj])
            self._masterlist.append(self)

    def get_masterlist(self):
        '''Return the master list that controls the prev/next relationships for
        the object'''

        return self._masterlist or Masterlist([self])

    #===========================================================================
    # Properties
    #===========================================================================
    @property
    def idx(self):
        try:
            return self._masterlist.index(self)
        except AttributeError:
            return None

    @property
    def next(self):
        try:
            L = self._masterlist
            return L[L.index(self) + 1]
        except (IndexError, AttributeError):
            return None

    @property
    def prev(self):
        try:
            L = self._masterlist
            idx = L.index(self)
            return L[idx - 1] if idx else None
        except (IndexError, AttributeError):
            return None

    @property
    def has_siblings(self):
        try:
            return len(self._masterlist or []) > 1
        except AttributeError:
            return False

    def get_siblings(self):
        return list(self._masterlist or [self])

    def get_siblings_next(self):
        '''A list of all siblings after itself'''

        try:
            return self._masterlist[self.idx + 1:]
        except AttributeError:
            return []

    def get_siblings_prev(self):
        '''Return a list of all siblings before itself'''

        try:
            return self._masterlist[:self.idx]
        except AttributeError:
            return []

    @property
    def parent(self):
        try:
            masterlist = self._masterlist
        except AttributeError:
            return None
        else:
            return getattr(masterlist, 'parent', None)

    @property
    def has_children(self):
        return False

class Container(Element):
    '''An element that have children'''

    def __init__(self):
        self._children = Masterlist([], self)

    @property
    def children(self):
        return self._children

    @property
    def has_children(self):
        return True

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.children.parent = self

class Masterlist(list):
    '''Organizes a group of objects with next/prev/parent interface into a 
    consistent list.
    
    There are few notable diferences between PrevNextLists and regular lists.
    First, duplicated elements are not allowed. The list represents a 
    sequence of prev/next associations and duplicated elements would become 
    circular references. For the same reason, mathematical operations are not
    allowed, since the list that shall represent these associations would become 
    ambiguous. 
    
    Usage
    -----

    Let us define a class that accept the prev/next interface in order to create
    a list of those objects

    >>> class pnstr(str, Element): pass
    >>> R, E, S, P, e, C, T = L = Masterlist(map(pnstr, 'RESPECT')); L
    ['R', 'E', 'S', 'P', 'E', 'C', 'T']
    
    Items know their siblings using the prev/next methods
    
    >>> print(R, R.next, P.prev, C.next)
    R E S T

    Items can be removed and insert in a Masterlist either using the regular
    list interface or calling the proper functions from its elements
    
    >>> P.unlink(); C.unlink(); L
    ['R', 'E', 'S', 'E', 'T']

    Insertions are also allowed

    >>> R.insert_prev(pnstr('P')); L
    ['P', 'R', 'E', 'S', 'E', 'T']

    Or even replace objects
    
    >>> deleted = L.pop()
    >>> e.replace_by(pnstr('LEY')); L
    ['P', 'R', 'E', 'S', 'LEY']
    
    Deleted items loose their siblings
    
    >>> deleted.has_siblings
    False
    
    Deepcopies preserve next/prev relationships
    
    >>> import copy
    >>> L2 = copy.deepcopy(L); L2
    ['P', 'R', 'E', 'S', 'LEY']

    We can clear a list to unlink all its elements
    
    >>> L.clear()
    ['P', 'R', 'E', 'S', 'LEY']
    >>> R.has_siblings
    False
    '''
    __slots__ = ['parent', '_cache']

    def __init__(self, data=None, parent=None):
        # Only accept parents of the correct type
        if not isinstance(parent, Element) and parent is not None:
            raise TypeError('invalid type for parent: %s' % type(parent).__name__)

        # Save variables and initialize
        super(Masterlist, self).__init__([])
        self.parent = parent
        self._cache = {}
        self.extend(data or [])


    # This is only a debug feature, probably not needed anymore
    if _sys.flags.debug:
        def _has_consistent_idx(self):
            correct = list(range(len(self)))
            return correct == sorted(self._cache.values()) == [ x.idx for x in self ]
    else:
        def _has_consistent_idx(self):
            return True

    def __contains__(self, obj):
        return id(obj) in self._cache

    def __delitem__(self, idx):
        if isinstance(idx, int):
            self.pop(idx)
        else:
            delidx = sorted((obj.idx for obj in self[idx]), reverse=True)
            for idx in delidx:
                del self[idx]

        # invariant checks
        assert self._has_consistent_idx()

    def __setitem__(self, idx, value):
        cache = self._cache
        current = self[idx]

        if value is current:
            return
        if id(value) in cache:
            raise ValueError('object already present in the list')
        if not isinstance(value, Element):
            raise TypeError('only Elements are accepted, got %s' % (type(value).__name__))

        value._set_masterlist(self)
        cache[id(value)] = idx = current.idx
        super(Masterlist, self).__setitem__(idx, value)
        del cache[id(current)]

        # invariant checks
        assert self._has_consistent_idx()

    def __copy__(self):
        L_copies = []
        for x in self:
            try:
                del x._masterlist
                cp = _copy.copy(x)
                if cp is x:
                    raise RuntimeError('improper __copy__ implementation: '
                                       'object and its copy cannot share identity')
                L_copies.append(cp)
            finally:
                x._masterlist = self

        L = Masterlist.__new__(type(self))
        L._cache = {}
        L._parent = self._parent
        L.extend(L_copies)
        return L

    def __deepcopy__(self, memo):
        L = Masterlist.__new__(type(self))
        L._cache = {}
        memo[id(self)] = L

        for x in self:
            try:
                del x._masterlist
                cp = _copy.deepcopy(x, memo)
                assert cp is not x, ('improper __deepcopy__ implementation: '
                                     'object and its copy cannot share identity')
                L.append(cp)
            finally:
                x._masterlist = self
        L.parent = None
        return L

    def __imul__(self, n):
        raise TypeError('arithmetical operations are not allowed')

    def __iadd__(self, n):
        raise TypeError('arithmetical operations are not allowed')

    def __add__(self):
        raise TypeError('arithmetical operations are not allowed')

    def append(self, value):
        '''L.append(value) -- append value to end'''

        cache = self._cache
        if id(value) in cache:
            raise ValueError('object already present in the list')
        if not isinstance(value, Element):
            raise TypeError('only Elements are accepted, got %s' % (type(value).__name__))

        value._set_masterlist(self)
        super(Masterlist, self).append(value)
        cache[id(value)] = len(self) - 1

        # invariant checks
        assert self._has_consistent_idx()

    def extend(self, seq):
        '''L.extend(iterable) -- extend list by appending elements from the iterable'''

        for obj in seq:
            self.append(obj)

        # invariant checks
        assert self._has_consistent_idx()

    def index(self, obj, start=None, stop=None):
        '''L.index(value) -> integer -- return first index of value. 
        Raises ValueError if the value is not present.'''

        try:
            idx = self._cache[id(obj)]
        except KeyError:
            raise ValueError('not in list: %r' % obj)
        if start is not None and idx > start:
            raise ValueError(obj)
        elif stop is not None and idx < stop:
            raise ValueError(obj)
        else:
            return idx

    def insert(self, idx, value):
        '''L.insert(index, value) -- insert object before index'''

        cache = self._cache
        if id(value) in cache:
            raise ValueError('object already present in the list')
        if not isinstance(value, Element):
            raise TypeError('only Elements are accepted, got %s' % (type(value).__name__))

        value._set_masterlist(self)
        super(Masterlist, self).insert(idx, value)
        cache[id(value)] = idx
        for i in range(idx + 1, len(self)):
            cache[id(self[i])] += 1

        # invariant checks
        assert self._has_consistent_idx()

    def pop(self, idx=None):
        '''L.pop(index) -> item -- remove and return item at index (default last).
        Raises IndexError if list is empty or index is out of range.'''

        cache = self._cache

        if idx is None:
            obj = super(Masterlist, self).pop()
            del cache[id(obj)]
        else:
            N = len(self)
            obj = super(Masterlist, self).pop(idx)
            idx = (idx if idx >= 0 else (N + idx))
            for i in range(idx, N - 1):
                cache[id(self[i])] -= 1
            del cache[id(obj)]

        del obj._masterlist

        # invariant checks
        assert self._has_consistent_idx()
        return obj

    def remove(self, value):
        '''L.remove(value) -- remove first occurrence of value.
        Raises ValueError if the value is not present.'''

        del self[self._cache[id(value)]]

        # invariant checks
        assert self._has_consistent_idx()

    def reverse(self):
        '''L.reverse() -- reverse *IN PLACE*'''

        cache = self._cache
        super(Masterlist, self).reverse()
        for i, obj in enumerate(self):
            cache[id(obj)] = i

        # invariant checks
        assert self._has_consistent_idx()

    def sort(self, key=None, reverse=False):
        '''L.sort(key=None, reverse=False) -- stable sort *IN PLACE*;'''

        cache = self._cache
        super(Masterlist, self).sort(key=key, reverse=reverse)
        for i, obj in enumerate(self):
            cache[id(obj)] = i

        # invariant checks
        assert self._has_consistent_idx()

    def clear(self):
        '''L.clear() -> list -- clear all objects in the list and return a list 
        of the cleared objects. This clear the next/prev association between 
        these objects.'''

        objects = list(self)
        del self[:]

        # invariant checks
        assert self._has_consistent_idx()
        return objects

if __name__ == '__main__':
    import doctest
    doctest.testmod()
