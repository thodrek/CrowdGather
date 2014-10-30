# Module containing util methods
import random
import itertools


# Flatten dictionary to list of elements
def flatten_dict(d):
    for k,v in d.items():
        if isinstance(v, dict):
            for item in flatten_dict(v):
                yield item
        else:
            yield v


def flatten_dict_keys(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            mergedItems = list(itertools.chain.from_iterable(list(flatten_dict(v))))
            items.append((new_key, mergedItems))
            items.extend(flatten_dict_keys(v, new_key, sep=sep))
        else:
            items.append((new_key, v))
    return items

def lattice_points_list(d):
    output = flatten_dict_keys(d)
    root = [('',list(itertools.chain.from_iterable(list(flatten_dict(d)))))]
    root.extend(output)
    return root

def lattice_point_product(l1,l2):
    tempProd = list(itertools.product(l1,l2))
    latticePointList = []
    for e in tempProd:
	key1 = e[0][0]
	key2 = e[1][0]
	items = []
	items.extend(e[0][1])
	items.extend(e[1][1])
	newkey = key1+"|"+key2
	latticePointList.append((newkey, items))
    return latticePointList


def cross(*args):
    ans = [[]]
    for arg in args:
        ans = [x+[y] for x in ans for y in arg]
    return ans

#Sampling without replacement. Choose n random elements from a list of (item, weight) tuples.
def sampleWOReplacement(l, k):
    l = sorted((random.random() * x[1], x[0]) for x in l)
    return l[-k:]
