__author__ = 'thodoris'

class PointEstimateNew:

    def __init__(self,latticePoint,querySize,excludeListSize):
        self.point = latticePoint

        # expected return variables
        self.querySize = querySize
        self.excludeListSize = excludeListSize

        # sampling variables
        self.oldSamples = []
        self.oldKValues = []
        self.freqCounters = []
        self.sampleSize  = []
        self.uniqueNumber = []

    # construct exclude list by taking random sample of size listSize
    def constructExcludeList(self):
        # take a random sample of size listSize from retrieved entries
        if self.excludeListSize >= len(self.point.distinctEntries):
            excludeList = self.point.distinctEntries
        else:
            excludeList = random.sample(self.point.distinctEntries,self.excludeListSize)
        return excludeList