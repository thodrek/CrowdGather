# Module containing util methods
import random


# Flatten dictionary to list of elements
def flatten_dict(d):
    for k,v in d.items():
        if isinstance(v, dict):
            for item in flatten_dict(v):
                yield item
        else:
            yield v


#Sampling without replacement. Choose n random elements from a list of (item, weight) tuples.
def sampleWOReplacement(l, k):
    l = sorted((random.random() * x[1], x[0]) for x in l)
    return l[-k:]