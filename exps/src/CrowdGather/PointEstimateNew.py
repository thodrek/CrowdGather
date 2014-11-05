__author__ = 'thodoris'
import numpy as np
import random
import sys
from utilities import functions
import scipy.optimize
import math

class PointEstimateNew:

    def __init__(self,latticePoint,querySize,excludeListSize):
        self.point = latticePoint

        # expected return variables
        self.querySize = querySize
        self.excludeListSize = excludeListSize

        # sampling variables
        self.oldSamples = []
        self.oldKValues = {}
        self.freqCounters = {}
        self.sampleSize  = 0.0
        self.uniqueNumber = 0.0
        self.oldK = None

    # construct exclude list by taking random sample of size listSize
    def constructExcludeList(self):
        # take a random sample of size listSize from retrieved entries
        if self.excludeListSize >= len(self.point.distinctEntries):
            excludeList = self.point.distinctEntries
        else:
            excludeList = random.sample(self.point.distinctEntries,self.excludeListSize)
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

    # estimate K prime
    def estimateKprime(self, newX):
        # create x and y values
        x = []
        y = []
        for v in self.oldKValues:
            x.append(v)
            y.append(self.oldKValues[v])
        x_ar = np.array(x)
        y_ar = np.array(y)
        initial_values = np.array([0.0,0.0,0.0])
        params, value, d = scipy.optimize.fmin_l_bfgs_b(functions.kappa_new_error, x0 = initial_values, args=(x_ar,y_ar), approx_grad=True)
        A, G, D = params
        return A/(1.0 + math.exp(-G*(newX - D)))

    # estimate P1
    def estimateP1(self):
        if 2 in self.freqCounters:
            N2 = self.freqCounters[2] + 1.0
        else:
            N2 = 1.0
        n = self.totalEntries()
        return 2.0*N2/(n+1)

    # estimate altered singletons
    def estimateAlteredSingletons(self):
        items = 0.0
        p1 = self.estimateP1()
        for k in range(self.querySize+1):
            mCk = math.factorial(self.querySize)/(math.factorial(k)*math.factorial(self.querySize-k))
            biProb = mCk*math.pow(p1,k)*math.pow(1.0-p1,self.querySize-k)
            dItems = k*biProb
            items += dItems
        return items

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

    # estimate return
    def estimateReturn(self):
        # construct excludeList
        excludeList = self.constructExcludeList()

        # update freq counters
        self.updateFreqCounterSampleSize(excludeList)

        # check if sample is empty
        if self.sampleSize == 0.0:
            if self.point.emptyPopulation == True:
                return 0.0
            else:
                return self.querySize

        # compute K
        f0, K = self.estimateF0_regression()
        self.oldKValues[self.sampleSize] = K
        self.oldK = K

        # compute return
        newSampleSize = self.sampleSize + self.querySize
        n = self.sampleSize
        Kprime = self.estimateKprime(newSampleSize)
        f1c = self.estimateAlteredSingletons()
        f1 = self.freqCounters[1]
        newItems = (K*f1/n - Kprime*(f1 - f1c)/newSampleSize)/(1.0 + Kprime/newSampleSize)
        return newItems