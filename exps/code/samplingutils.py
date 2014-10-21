# Module containing sampling functions for hierarchies
import random


# Flatten dictionary to list of elements
def flatten_dict(d):
    for k,v in d.items():
        if isinstance(v, dict):
            for item in flatten_dict(v):
                yield item
        else:
            yield v

# Weighted Sampling without Replacement
def weightedSelectionWithoutReplacement(l, k):
    """Selects without replacement n random elements from a list of (weight, item) tuples."""
    l = sorted((random.random() * x[2], x[0]) for x in l)
    #l = sorted((random.random(), x[0]) for x in l)
    return l[-k:]

# Sample k-elements from underlying distribution
# Input: Dictionary containing items
def sampleK(d,k):
    entryList = list(flatten_dict(d))
    sample = weightedSelectionWithoutReplacement(entryList,k)
    itemSample = list(x[1] for x in sample)
    return itemSample

# Sample k-elements from underlying
# Input: List containing items
def sampleKList(entryList,k):
    sample = weightedSelectionWithoutReplacement(entryList,k)
    itemSample = list(x[1] for x in sample)
    return itemSample

def totalPopulation(d):
    entryList = list(flatten_dict(d))
    return len(entryList)


def getTotalEntries(d):
    entryList = list(flatten_dict(d))
    return entryList


def findChildrenNodes(hierarchy,entry):
    childrenWithEntry = []
    for child in hierarchy:
        containedEntries = list(flatten_dict(hierarchy[child]))
        containedEntryIds = list(x[0] for x in containedEntries)
        if entry in containedEntryIds:
            childrenWithEntry.append(child)

    return childrenWithEntry


def belongsTo(hierarchyNode, entry):
    entries = list(flatten_dict(hierarchyNode))
    entryIDs = list(zip(*entries)[0])
    if entry in entryIDs:
        return 1
    else:
        return 0
