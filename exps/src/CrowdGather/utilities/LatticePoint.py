__author__ = 'thodrek'
import genutils

class LatticePoint:
    def __init__(self, key, db, hDesc, lattice):
        self.key = key
        self.lattice = lattice
        self.items = None
        self.parents = []
        self.descendants = []
        self.db = db
        # set hValues
        hValues_list = key.split('|')
        self.hValues = {}
        self.totalAssignedValues = 0
        for i in range(len(hDesc)):
            self.hValues[hDesc[i]] = hValues_list[i]
            if hValues_list[i] != '':
                self.totalAssignedValues += 1

    def getTotalAssignedValues(self):
        return self.totalAssignedValues

    def getParents(self):
            return self.parent

    def getDescendants(self):
            return self.descendants

    def assignParent(self, newparent):
        self.parents.append(newparent)

    def assignDescendant(self, newdesc):
        self.descendants.append(newdesc)

    def getKey(self):
        return self.key

    def retrieveSample(self, sampleSize):
        # if itemList is empty fetch it from DB
        if not self.items:
            self.items = self.__constructPopulation()

        # retrieve sample
        sample = genutils.sampleWOReplacement(self.items,sampleSize)

        return sample

    def __constructPopulation(self):
            # retrieve item set associated with lattice point
            itemSet = self.db.getKeySET(self.key)
            itemList = self.lattice.getItemWeights(itemSet)
            return itemList


    def containsItem(self,item):
        # check if current point is the root
        if self.key == '|'.join(['']*len(self.hValues)):
            return True

        # if not the root fetch the attributes of the item
        for h in self.hValues:
            if self.lattice.itemInfo[item][h].startswith(self.hValues[h]):
                return True

        return False

    def findMatches(self, itemList):
        # iterate over items and keep matches
        matches = []
        for item in itemList:
            if self.containsItem(item):
                matches.append(item)

