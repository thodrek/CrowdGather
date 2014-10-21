from utilities import genutils

__author__ = 'thodoris'
"""
This module generates a dictionary corresponding to
the yelp hierarchy in data/yelp_academic_dataset_business.json.

It also provides methods for sampling the yelp hierarchy

"""

import json


# Define the YelpData class

class YelpData:
    def __init__(self):
        self.datafile = "data/yelp_academic_dataset_business.json"
        # Read input data
        dataCursor = open(self.datafile,'r')
        self.jsonData = []
        for l in dataCursor:
            self.jsonData.append(json.loads(l))

        # Create business dictionary
        self.busDict = self.initHierarchy()

        # Create business hierarchy from dictionary
        self.busH = self.createHierarchy(self.busDict)


    def getBusHierarchy(self):
        return self.busH

    def initHierarchy(self):
        # Initialize business hierarchy
        business = {}
        business['N/A'] = {}

        # Iterate over file entries and populate hierarchies
        for e in self.jsonData:
            # Extract entry information
            business_id = e['business_id']
            review_count = e['review_count']
            stars = e['stars']
            business_cat = e['categories']

            # If entry's category is not specified assign to generic category N/A
            if len(business_cat) == 0:
                business['N/A'][business_id]= [business_id,float(stars),float(review_count)]

            # Populate business hierarchy
            for cat in business_cat:
                if (cat not in business):
                    business[cat] = {}
                    business[cat][business_id]= [business_id,float(stars),float(review_count)]
                else:
                    business[cat][business_id]= [business_id,float(stars),float(review_count)]

        return business

    def createHierarchy(self,dict):
        # Determine internal vs leaf nodes
        internalNode = {}
        for cat1 in dict:
            for cat2 in dict:
                if cat1 != cat2:
                    cat1Entries = set(dict[cat1].keys())
                    cat2Entries = set(dict[cat2].keys())
                    if cat2Entries.issubset(cat1Entries):
                        if cat1 not in internalNode:
                            internalNode[cat1] = []
                            internalNode[cat1].append(cat2)
                        else:
                            internalNode[cat1].append(cat2)

        # Build hierarchy
        fHierarchy = {}
        fHierarchy['root'] = {}
        for cat in internalNode:
            if len(internalNode[cat]) > 1:
                fHierarchy['root'][cat] = {}
                for inCat in internalNode[cat]:
                    fHierarchy['root'][cat][inCat] = {}
                    for bId in dict[inCat]:
                            fHierarchy['root'][cat][inCat][bId] = dict[inCat][bId]

        return fHierarchy

    # Examine if an entry belongs in a node
    def entryInNode(self,hNode,entry):
        entries = list(genutils.flatten_dict(hNode))
        entryIDs = list(zip(*entries)[0])
        if entry in entryIDs:
            return 1
        else:
            return 0

    # Find all the childrend nodes of a node h in the hierarchy that contain a given entry
    def childrenNodesWithEntry(self,hNode,entry):
        childrenWithEntry = []
        for child in hNode:
            if self.entryInNode(child,entry) == 1:
                childrenWithEntry.append(child)
        return childrenWithEntry


class YelpSample:
    def __init__(self, yd, hNode, popularity = "rating"):
        self.YelpData = yd
        self.hNode = hNode
        self.population = self.generatePopulation(hNode,popularity)
        self.popularity = popularity

    def generatePopulation(self,hNode,popularity = "rating"):
        visited = []
        uniqueEntries = []
        for e in list(genutils.flatten_dict(hNode)):
            if e[0] not in visited:
                if popularity == "reviews":
                    uniqueEntries.append([e[0],e[2]])
                else:
                    uniqueEntries.append([e[0],e[1]])
            visited.append(e[0])
        return uniqueEntries


    def generatePopulationwithExList(self,hNode,exList,popularity="rating"):
        totalEntries = self.generatePopulation(hNode,popularity="rating")
        finalEntries = []
        for e in totalEntries:
            if e[0] not in exList:
                finalEntries.append(e)
        return finalEntries


    #Sample k-items from a hierarchy node
    def sampleK(self,k):
        sample = genutils.sampleWOReplacement(self.population,k)
        items = list(x[1] for x in sample)
        return items

    def sampleKwithExList(self,exList,k):
        newPopulation = self.generatePopulationwithExList(self.hNode,exList,self.popularity)
        sample = genutils.sampleWOReplacement(newPopulation,k)
        items = list(x[1] for x in sample)
        return items

    def totalPopulation(self):
        return len(self.population)

    def getAllEntries(selfs):
        return self.population


