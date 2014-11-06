__author__ = 'thodrek'
import genutils
import copy

class LatticePoint:
    def __init__(self, key, db, hDesc, lattice, samplingHistory=False):
        # set lattice point details
        self.key = key
        self.lattice = lattice
        self.db = db

        # set lattice point neighborhood
        self.parents = []
        self.descendants = []

        # set hValues
        hValues_list = key.split('|')
        self.hValues = {}
        self.totalAssignedValues = 0
        for i in range(len(hDesc)):
            self.hValues[hDesc[i]] = hValues_list[i]
            if hValues_list[i] != '':
                self.totalAssignedValues += 1

        # set lattice real population
        self.items = None

        # set lattice sampling results
        self.retrievedEntries = []
        self.distinctEntries = set([])
        self.entryFrequencies = {}

        # flags for estimators
        self.emptyPopulation = False

        # keep sampling log
        self.samplingHistory = samplingHistory
        self.sampleLogs = []
        self.distinctEntryLogs = []
        self.entryFrequencyLogs = []

        # initialize childrenDistribution
        self.childrenWeights = {}

    def getTotalAssignedValues(self):
        return self.totalAssignedValues

    def getParents(self):
        return self.parents

    def getDescendants(self):
        return self.descendants

    def assignParent(self, newparent):
        self.parents.append(newparent)

    def assignDescendant(self, newdesc):
        self.descendants.append(newdesc)

    def getKey(self):
        return self.key

    def retrieveSample(self, sampleSize, excludeList):

        # if itemList is empty fetch it from DB
        if not self.items:
            self.items = self.__constructPopulation()

        # retrieve sample
        # update sampling population to consider excludeList
        if len(excludeList) > 0:
            popItems = self.populationWithExcludeList(set(excludeList))
            sampleRaw = genutils.sampleWOReplacement(popItems,sampleSize)
        else:
            sampleRaw = genutils.sampleWOReplacement(self.items,sampleSize)
        sample = list(x[1] for x in sampleRaw)

        # check if sample is empty
        if len(sample) == 0.0:
            self.emptyPopulation = True
            self.emptyMessageDescendants()
        else:
            # update local sampling results
            self.__updateSamplingResults(sample)
            # propagate sampled items to children
            msgs = self.propagateSamples(sample)
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
            if not (self.lattice.itemInfo[item][h].startswith(self.hValues[h]) or self.hValues[h] == ''):
                return False

        return True

    def findMatches(self, itemList):
        # iterate over items and keep matches
        matches = []
        for item in itemList:
            if self.containsItem(item):
                matches.append(item)
        return matches

    def __updateSamplingResults(self,sample):
        # update unique and total entry lists
        self.retrievedEntries.extend(sample)
        self.distinctEntries |= set(sample)

        # update entry counters
        for id in sample:
            if id not in self.entryFrequencies:
                self.entryFrequencies[id] = 1
            else:
                self.entryFrequencies[id] += 1

        # update children weights
        self.updateChildrenDistr(sample)


    def receiveIndirectItem(self,item):
        newSample = [item]
        self.__updateSamplingResults(newSample)
        return True

    def propagateSamples(self,sample):
        msgReceived = 0
        for item in sample:
            affectedLatticePoints = self.findKeysForItem(item)
            for p_key in affectedLatticePoints:
                    if p_key == self.key:
                        continue
                    if self.lattice.points[p_key].receiveIndirectItem(item):
                        msgReceived += 1
        return msgReceived

    def receiveEmptyMsg(self):
        self.emptyPopulation = True
        self.emptyMessageDescendants()

    def emptyMessageDescendants(self):
        for p in self.descendants:
            p.receiveEmptyMsg()

    def findKeysForItem(self,item):
        # construct hierarchical attribute information from item description
        itemHdicts = []
        for h in self.lattice.hDesc:
            # retrieve item value for attribute h
            attrValue = self.lattice.itemInfo[item][h]
            # break down to dict
            newAttrDict = {}
            attrValueTokens = attrValue.split('_')
            runningDict = newAttrDict
            for i in range(len(attrValueTokens)):
                token = attrValueTokens[i]
                if i == len(attrValueTokens)-1:
                    runningDict[token] = []
                else:
                    runningDict[token] = {}
                runningDict = runningDict[token]
            itemHdicts.append(newAttrDict)

        # perform cross product to find all lattice point relevant to item
        itemHLists = [genutils.lattice_points_list(h) for h in itemHdicts]
        point_list = genutils.cross(*itemHLists)
        point_keys = []
        for point in point_list:
            point_key = point[0][0]
            for idx in range(1,len(itemHdicts)):
                point_key += '|'+point[idx][0]
            point_keys.append(point_key)

        return point_keys

    def populationWithExcludeList(self,excludeList):
        populationItems = []
        for item in self.items:
            if item[0] not in excludeList:
                populationItems.append(item)
        return populationItems

    def logSamplingHistory(self):
        # keep sampling log
        self.sampleLogs.append(self.retrievedEntries)
        self.distinctEntryLogs.append(self.distinctEntries)
        self.entryFrequencyLogs.append(self.etr)

    def clearSampledPopulation(self):
        del self.retrievedEntries[:]
        self.distinctEntries.clear()
        self.entryFrequencies.clear()

        # flags for estimators
        self.emptyPopulation = False

    def updateChildrenDistr(self, sample):
        for item in sample:
            for d in self.descendants:
                if d.containsItem(item):
                    if d in self.childrenWeights:
                        self.childrenWeights[d] += 1.0
                    else:
                        self.childrenWeights[d] = 1.0

    def childrenTotalWeight(self):
        totalWeight = 0.0
        for d in self.childrenWeights:
            totalWeight += self.childrenWeights[d]
        return totalWeight