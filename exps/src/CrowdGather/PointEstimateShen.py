__author__ = 'thodrek'
import random
import sys
from utilities import functions
import numpy as np
import scipy.optimize
import numpy.random as npr

class PointEstimateShen:

    def __init__(self,latticePoint,querySize,excludeListSize,estMethod):
        self.point = latticePoint

        # expected return variables
        self.querySize = querySize
        self.excludeListSize = excludeListSize

        # sampling variables
        self.freqCounters = {}
        self.sampleSize = 0.0
        self.uniqueNumber = 0.0
        self.oldK = None

        if estMethod == "chao92" or estMethod == "shenRegression":
            self.estMethod = estMethod
        else:
            print "Invalid estimator specified for expected return"
            sys.exit(-1)


    def __del__(self):
        self.freqCounters.clear()

    def clear(self):
        self.freqCounters.clear()

    # methods to retrieve characteristics of local sample
    def uniqueEntries(self):
        return len(self.point.distinctEntries)

    def totalEntries(self):
        return len(self.point.retrievedEntries)

    # construct exclude list by taking random sample of size listSize
    def constructExcludeList(self, distinctEntries):
        # take a random sample of size listSize from retrieved entries
        if self.excludeListSize >= len(distinctEntries):
            excludeList = distinctEntries
        else:
            excludeList = random.sample(distinctEntries,self.excludeListSize)
        return excludeList

    # compute frequency counters
    def updateFreqCounterSampleSize(self,excludeList,entryFrequencies):
        self.sampleSize = 0.0
        self.uniqueNumber = 0.0
        self.freqCounters.clear()
        if len(entryFrequencies) > 0.0:
            maxF = max(entryFrequencies.values())
            for f in range(1,maxF+1):
                self.freqCounters[f] = 0.0

            for e in entryFrequencies:
                if e not in excludeList:
                    f = entryFrequencies[e]
                    self.freqCounters[f] += 1.0
                    self.sampleSize += float(f)
                    self.uniqueNumber += 1.0

    # estimate return
    def estimateReturn(self,strataOption=False):
        # construct excludeList
        excludeList = self.constructExcludeList(self.point.distinctEntries)

        # update freq counters
        self.updateFreqCounterSampleSize(excludeList,self.point.entryFrequencies)

        # check if sample is empty
        if self.sampleSize == 0.0:
            if self.point.emptyPopulation == True:
                return 0.0
            else:
                return self.querySize

        # check if exclude list contains the entire sample
        if len(excludeList) == len(self.point.distinctEntries):
            return self.querySize

        # compute query return
        if strataOption and len(self.point.childrenWeights) > 0:
            return self.estimateStratifiedReturn(excludeList)
        return self.shenEstimator(self.querySize,self.estMethod)

    # estimate return with variance
    def estimateReturnBootStrap(self,distinctEntries,entryFrequencies):
        # construct excludeList
        excludeList = self.constructExcludeList(distinctEntries)

        # update freq counters
        self.updateFreqCounterSampleSize(excludeList,entryFrequencies)

        # check if sample is empty
        if self.sampleSize == 0.0:
            if self.point.emptyPopulation == True:
                return 0.0
            else:
                return self.querySize

        # check if exclude list contains the entire sample
        if len(excludeList) == len(self.point.distinctEntries):
            return self.querySize

        # compute query return
        return self.shenEstimator(self.querySize,self.estMethod)

    # auxiliary functions
    def estimateCoverage(self):
        # Good-Turing estimator
        f1 = self.freqCounters[1]
        n = self.sampleSize
        return 1.0 - f1/(n+1)

    def estimateGamma2(self, Chat):
        c = self.uniqueNumber
        n = self.sampleSize

        gamma_sum = 0.0
        for f in self.freqCounters:
            gamma_sum += float(f)*(float(f)-1.0)*self.freqCounters[f]
        if n == 1:
            return 0.0
        gammasq = (c/Chat)*gamma_sum/(n*(n-1.0)) - 1.0
        if gammasq < 0.0:
            return 0.0
        return gammasq

    def estimateF0_Chao92(self, Chat):
        c = self.uniqueNumber
        gammasq = self.estimateGamma2(Chat)
        n = self.sampleSize

        NChao92 = c/Chat + n*(1.0-Chat)*gammasq/Chat

        return NChao92 - c

    # methods to estimate unseen items
    def computeKcurrent(self,upperK=None):
        # sample size
        n = self.sampleSize

        # create (x,y) values
        x = []
        y = []
        for f in self.freqCounters:
            if f+1 in self.freqCounters:
                y_new = (n-float(f))*self.freqCounters[f]/(float(f)+1.0)*(self.freqCounters[f+1] + 1.0)
                x.append(float(f))
                y.append(y_new)
            else:
                y_new = (n-float(f))*self.freqCounters[f]/(float(f)+1.0)*(0.0 + 1.0)
                x.append(float(f))
                y.append(y_new)
        # Not enough data to estimate K
        if len(x) < 1.0:
            return None

        # Estimate K using lbfgsb
        x_ar = np.array(x)
        y_ar = np.array(y)
        initial_values = np.array([self.uniqueNumber,0.0,0.0])
        bounds = [(upperK, None), (None, 0.0), (0.0, None)]

        params, value, d = scipy.optimize.fmin_l_bfgs_b(functions.kappa_error, x0 = initial_values, args=(x_ar,y_ar), bounds = bounds, approx_grad=True)
        return params[0]

    def estimateF0_regression(self):
        K = self.computeKcurrent(self.oldK)
        # sample size
        n = self.sampleSize
        # singletons
        f1 = 0.0
        if 1 in self.freqCounters:
            f1 = self.freqCounters[1]
        return K*f1/n,K

    # estimate return based on Shen estimator
    def shenEstimator(self,querySize,estimator):
        #estimate coverage
        Chat = self.estimateCoverage()

        #estimate unseen
        if estimator == "chao92":
            f0 = self.estimateF0_Chao92(Chat)
        else:
            f0, self.oldK = self.estimateF0_regression()

        #estimate new
        gain = f0*(1.0 - (1.0 - (1.0 - Chat)/(f0 + 1.0))**querySize)
        return gain


    # normalized return
    def normalizedReturn(self):
        return self.estimateReturn()/float(self.querySize)

    # cost of estimator
    def computeCost(self,maxQuerySize,maxExListSize):
        pointSpecificity = self.point.totalAssignedValues

        w_Q_Size = 1.0
        Q_value = float(self.querySize)/float(maxQuerySize)

        w_E_Size = 1.0
        E_value = float(self.excludeListSize)/float(maxExListSize)

        w_Spec = 1.0
        S_value = float(pointSpecificity)/3.0

        cost = (w_Q_Size*Q_value + w_E_Size*E_value + S_value*w_Spec)/(w_Q_Size + w_E_Size + w_Spec)
        return cost

    # break excludelist to children
    def excludeListToChildren(self,excludeList):
        childrenExcludeLists = {}
        for d in self.point.descendants:
            childrenExcludeLists[d] = []
            for item in excludeList:
                if d.containsItem(item):
                    childrenExcludeLists[d].append(item)
        return childrenExcludeLists

    def querySizeToChildren(self):
        childrenQuerySizes = {}
        totalWeight = self.point.childrenTotalWeight()
        for d in self.point.descendants:
            querySize = float(self.querySize)*self.point.childrenWeights[d]/totalWeight
            childrenQuerySizes[d] = querySize
        return childrenQuerySizes

    def estimateStratifiedReturn(self,excludeList):
        gain = 0.0
        totalWeight = self.point.childrenTotalWeight()
        for d in self.point.childrenWeights:
            childExList = []
            # compute child's exclude list
            for item in excludeList:
                if d.containsItem(item):
                    childExList.append(item)
            childQuerySize = int(round(float(self.querySize)*self.point.childrenWeights[d]/totalWeight))
            # instanciate new estimator
            childGainEst = PointEstimateShen(d,childQuerySize,childExList,self.estMethod)
            childGain = childGainEst.estimateReturn()
            gain += childGain
            childGainEst.clear()
            del childExList[:]
        return gain

    def bootstrapVariance(self, num_samples):
        # grap retrieved items from lattice point
        data = np.array(self.point.retrievedEntries)
        n = len(data)
        # generate bootstrapped samples
        idx = npr.randint(0, n, (num_samples, n))
        samples = data[idx]

        # initialize return estimates
        returnEstimates = []

        # iterate over samples and compute estimated return
        for i in range(num_samples):
            newSample = list(samples[i])
            newDistinct = set(newSample)
            newEntryFreqs = {}
            for id in newSample:
                if id not in newEntryFreqs:
                    newEntryFreqs[id] = 1
                else:
                    newEntryFreqs[id] += 1

            # get new estimate
            newReturn = self.estimateReturnBootStrap(newDistinct,newEntryFreqs)
            returnEstimates.append(newReturn)
            del newSample[:]
            newDistinct.clear()
            newEntryFreqs.clear()
        variance = np.var(np.array(returnEstimates))
        mean = np.mean(np.array(returnEstimates))
        alpha = 0.05
        statList = np.sort(returnEstimates)
        upperValue = statList[int((1-alpha/2.0)*num_samples)]
        return upperValue, mean, variance

    # take action
    def takeAction(self):

        # construct excludeList
        excludeList = self.constructExcludeList(self.point.distinctEntries)

        # store old unique
        oldUnique = len(self.point.distinctEntries)

        # retrieve sample from underlying node
        s = self.point.retrieveSample(self.querySize, excludeList)

        # store new unique
        newUnique = len(self.point.distinctEntries)

        # compute gain
        gain = newUnique - oldUnique
        return gain

    def estimateGain(self,upper=False):
        gain = self.estimateReturn()
        upperValue = gain
        if upper and len(self.point.retrievedEntries) > 0.0:
            upperValue, gain, variance = self.bootstrapVariance(100)
        else:
            variance = 0.0
        return gain, variance, upperValue