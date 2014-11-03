__author__ = 'thodrek'
import random
import sys
from utilities import functions
import numpy as np
import scipy.optimize

class PointEstimateShen:

    def __init__(self,latticePoint,querySize,excludeListSize):
        self.point = latticePoint

        # expected return variables
        self.querySize = querySize
        self.excludeListSize = excludeListSize

        # sampling variables
        self.freqCounters = {}
        self.sampleSize = 0.0
        self.uniqueNumber = 0.0
        self.oldK = None


    # methods to retrieve characteristics of local sample
    def uniqueEntries(self):
        return len(self.point.distinctEntries)

    def totalEntries(self):
        return len(self.point.retrievedEntries)

    # construct exclude list by taking random sample of size listSize
    def constructExcludeList(self,listSize):
        # take a random sample of size listSize from retrieved entries
        excludeList = random.sample(self.point.distinctEntries,listSize)
        return excludeList

    # compute frequency counters
    def updateFreqCounterSampleSize(self,excludeList):
        self.sampleSize = 0.0
        self.uniqueNumber = 0.0
        self.freqCounters.clear()
        if len(self.point.entryFrequencies) > 0.0:
            maxF = max(self.point.entryFrequencies.values())
            for f in range(1,maxF+1):
                self.freqCounters[f] = 0.0

            for e in self.point.entryFrequencies:
                if e not in excludeList:
                    f = self.point.entryFrequencies[e]
                    self.freqCounters[f] += 1.0
                    self.sampleSize += float(f)
                    self.uniqueNumber += 1.0

    # estimate return
    def estimateReturn(self,querySize,excludeListSize,estimator = "chao92"):
        # construct excludeList
        excludeList = self.constructExcludeList(excludeListSize)

        # update freq counters
        self.updateFreqCounterSampleSize(excludeList)

        # check if sample is empty
        if self.sampleSize == 0.0:
            if self.point.emptyPopulation == True:
                return 0.0
            else:
                return querySize

        # compute query return
        if estimator == "chao92" or estimator == "shenRegression":
            return self.shenEstimator(querySize,estimator)
        else:
            print "Invalid estimator specified for expected return"
            sys.exit(-1)

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