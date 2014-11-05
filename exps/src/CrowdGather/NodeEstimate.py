from utilities import functions

__author__ = 'thodrek'
import numpy as np
import scipy.optimize
import sys
import math
import random

class Estimate:
    def __init__(self,hNode,exListSize,querySize):
        # underlying node for which we are estimating the return
        self.hNode = hNode

        # content variables
        self.distinctEntries = set([])
        self.allEntries = []
        self.entryFrequencies = {}
        self.freqCounters = {}
        self.freqItems = {}

        # exclude list variables
        self.exListSize = exListSize
        self.excludeList = []

        # expected return variables
        self.expectedReturn = querySize


        # store K history values
        self.prevKvalues = {}

        # sampling history variables
        self.prevSamples = []
        self.prevKvalues_woEL = []
        self.prevKvalues_wEL = []



    # methods to update local sample
    def uniqueEntries(self):
        return len(self.distinctEntries)

    def totalEntries(self):
        return len(self.allEntries)

    def getFreqCounters(self):
        return self.freqCounters

    def updateFreqCounters(self):
        self.freqCounters = {}
        self.freqItems = {}
        maxF = max(self.entryFrequencies.values())
        for f in range(1,maxF+1):
            self.freqCounters[f] = 0.0
            self.freqItems[f] = []

        for e in self.entryFrequencies:
            f = self.entryFrequencies[e]
            self.freqCounters[f] += 1.0
            self.freqItems[f].append(e)

    def extendSample(self, newEntries):
        # first remove items from excludeList
        for e in self.excludeList:
            self.distinctEntries.remove(e)
            del self.entryFrequencies[e]
            while e in self.allEntries:
                self.allEntries.remove(e)

        # update unique and total entry lists
        self.allEntries.extend(newEntries)
        self.distinctEntries |= set(newEntries)

        # update entry counters
        for e in newEntries:
            if e not in self.entryFrequencies:
                self.entryFrequencies[e] = 1
            else:
                self.entryFrequencies[e] += 1

        # update frequency counters
        self.updateFreqCounters()

        # update exclude list
        self.constructExcludeList()


    # methods to estimate unseen items
    def computeKcurrent(self,upperK=None):
        # sample size
        n = float(len(self.allEntries))

        # create (x,y) values
        x = []
        y = []
        for f in self.freqCounters:
            if f+1 in self.freqCounters:
                y_new = (n-float(f))*self.freqCounters[f]/(float(f)+1.0)*(self.freqCounters[f+1] + 1.0)
                x.append(float(f))
                y.append(y_new)
        # Not enough data to estimate K
        if len(x) < 1.0:
            return None

        # Estimate K using lbfgsb
        x_ar = np.array(x)
        y_ar = np.array(y)
        initial_values = np.array([len(self.distinctEntries),0.0,0.0])
        bounds = [(upperK, None), (None, 0.0), (0.0, None)]

        params, value, d = scipy.optimize.fmin_l_bfgs_b(functions.kappa_error, x0 = initial_values, args=(x_ar,y_ar), bounds = bounds, approx_grad=True)
        return params[0]

    def estimateF0_regression(self,upperK):
        K = self.computeKcurrent(upperK)
        # sample size
        n = float(len(self.allEntries))
        # singletons
        f1 = 0.0
        if 1 in self.freqCounters:
            f1 = self.freqCounters[1]
        return K*f1/n,K

    def estimateF0_wo_replacement(self,w,r):
        f1 = self.freqCounters[1]
        f2 = self.freqCounters[2]
        return f1*f1/(2*w*f2 + r*f1)

    def estimateF0_Chao92(self):
        Chat = self.estimateCoverage()
        c = self.uniqueEntries()
        gammasq = self.estimateGamma2()
        n = self.totalEntries()

        NChao92 = c/Chat + n*(1.0-Chat)*gammasq/Chat

        return NChao92 - c


    def estimateCoverage(self):
        # Good-Turing estimator
        f1 = self.freqCounters[1]
        n = float(len(self.allEntries))
        return (1.0 - f1/n)


    def estimateGamma2(self):
        Chat = self.estimateCoverage()
        c = self.uniqueEntries()
        n = self.totalEntries()

        gamma_sum = 0.0
        for f in self.freqCounters:
            gamma_sum += float(f)*(float(f)-1.0)*self.freqCounters[f]
        gammasq = (c/Chat)*gamma_sum/(n*(n-1.0)) - 1.0
        if gammasq < 0.0:
            return 0.0
        return gammasq

    # methods to estimate new return
    def estimateReturn(self,querySize,unseenEstimator = "chao92", *args):
        #estimate coverage
        Chat = self.estimateCoverage()

        #estimate unseen
        f0 = 0.0
        if unseenEstimator == "chao92":
            f0 = self.estimateF0_Chao92()
        elif unseenEstimator == "chao2012":
            w = args[0]
            r = args[1]
            f0 = self.estimateF0_wo_replacement(w,r)
        elif unseenEstimator == "regression":
            upperK = args[0]
            f0 = self.estimateF0_regression(upperK)[0]
        else:
            print "Invalid estimator specified"
            sys.exit(-1)

        #estimate new
        newItems = f0*(1.0 - (1.0 - (1.0 - Chat)/(f0 + 1.0))**querySize)
        return newItems


    # methods for new return estimator

    def storeOldK(self,x,K):
        self.prevKvalues[x] = K

    def estimateKprime(self, newX):
        # create x and y values
        x = []
        y = []
        for v in self.prevKvalues:
            x.append(v)
            y.append(self.prevKvalues[v])
        x_ar = np.array(x)
        y_ar = np.array(y)
        initial_values = np.array([0.0,0.0,0.0])
        params, value, d = scipy.optimize.fmin_l_bfgs_b(functions.kappa_new_error, x0 = initial_values, args=(x_ar,y_ar), approx_grad=True)
        A, G, D = params
        return A/(1.0 + math.exp(-G*(newX - D)))

    def estimateP1(self):
        if 2 in self.freqCounters:
            N2 = self.freqCounters[2] + 1.0
        else:
            N2 = 1.0
        n = self.totalEntries()
        return 2.0*N2/(n+1)

    def estimateP(self,querySize):
        p = 0.0
        p1 = self.estimateP1()
        f1 = self.freqCounters[1]
        for k in range(querySize+1):
            mCk = math.factorial(querySize)/(math.factorial(k)*math.factorial(querySize-k))
            biProb = mCk*math.pow(p1,k)*math.pow(1.0-p1,querySize-k)
            dp = (1.0 - (1.0 - 1/f1)**k)*biProb
            p += dp
        return p

    def estimateAlteredSingletons(self, querySize):
        items = 0.0
        p1 = self.estimateP1()
        for k in range(querySize+1):
            mCk = math.factorial(querySize)/(math.factorial(k)*math.factorial(querySize-k))
            biProb = mCk*math.pow(p1,k)*math.pow(1.0-p1,querySize-k)
            dItems = k*biProb
            items += dItems
        print "Singletons that changed = ", items
        return items

    def estimateReturnNew(self, querySize, K):
        newSampleSize = self.totalEntries() + querySize
        n = self.totalEntries()
        Kprime = self.estimateKprime(newSampleSize)
        f1c = self.estimateAlteredSingletons(querySize)
        f1 = self.freqCounters[1]
        newItems = (K*f1/n - Kprime*(f1 - f1c)/newSampleSize)/(1.0 + Kprime/newSampleSize)
        return newItems


    # Methods related to exclude list
    def constructExcludeList(self):
        k = self.exListSize
        freqs = []
        freqs.extend(self.freqCounters.keys())
        freqs.sort(reverse=True)
        self.excludeList = []

        for f in freqs:
            # add more items in exclude list
            if len(self.excludeList) == k:
                break
            if len(self.excludeList) + self.freqCounters[f] <= k:
                # add all items
                self.excludeList.extend(self.freqItems[f])
            else:
                # add only a subset of items
                candItems = sorted((random.random(), x) for x in self.freqItems[f])
                m = k - len(self.excludeList)
                excludeItems = list(x[1] for x in candItems[-m:])
                self.excludeList.extend(excludeItems)

    def getExcludeList(self):
        return self.excludeList



