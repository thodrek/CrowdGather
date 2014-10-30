__author__ = 'thodrek'


class LatticePoint:
    def __init__(self, key, db, hDesc):
        self.key = key
        self.items = []
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


