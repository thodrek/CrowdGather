__author__ = 'thodoris'
import numpy as np
import random
import sys
from utilities import functions
import scipy.optimize
import math
import numpy.random as npr
from inputData import points

class PointEstimateNew:

    def __init__(self,latticePointId,querySize,excludeListSize, childrenDistribution=False):
        self.pointId = latticePointId

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
        self.timesSelected = 1.0

    # construct exclude list by taking random sample of size listSize
    def constructExcludeList(self,distinctEntries):
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
        n = self.sampleSize
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
    def estimateReturn(self,strataOption=False,tempEstimate=False):

        # if temp estimation generate K history
        if tempEstimate:
            self.compute_K_History()

        # construct excludeList
        excludeList = self.constructExcludeList(points[self.pointId].distinctEntries)

        # update freq counters
        self.updateFreqCounterSampleSize(excludeList,points[self.pointId].entryFrequencies)

        # check if sample is empty
        if self.sampleSize == 0.0:
            if points[self.pointId].emptyPopulation == True:
                return 0.0
            else:
                return self.querySize

        # compute K
        f0, K = self.estimateF0_regression()
        self.oldKValues[self.sampleSize] = K
        self.oldK = K

        # check if exclude list contains the entire sample
        if len(excludeList) == len(points[self.pointId].distinctEntries):
            return self.querySize

        # compute query return
        if strataOption and len(points[self.pointId].childrenWeights) > 0:
            return self.estimateStratifiedReturn(excludeList)

        # compute return
        newSampleSize = self.sampleSize + self.querySize
        n = self.sampleSize
        Kprime = self.estimateKprime(newSampleSize)
        f1c = self.estimateAlteredSingletons()
        f1 = self.freqCounters[1]
        newItems = (K*f1/n - Kprime*(f1 - f1c)/newSampleSize)/(1.0 + Kprime/newSampleSize)
        return newItems

    # estimate return with variance
    def estimateReturnBootStrap(self,distinctEntries,entryFrequencies):

        # construct excludeList
        excludeList = self.constructExcludeList(distinctEntries)

        # update freq counters
        self.updateFreqCounterSampleSize(excludeList,entryFrequencies)
        # check if sample is empty
        if self.sampleSize == 0.0:
            if points[self.pointId].emptyPopulation == True:
                return 0.0, self.oldK
            else:
                #return self.querySize, self.oldK
                return 1.0, self.oldK
        # compute K
        f0, K = self.estimateF0_regression()
        # check if exclude list contains the entire sample
        #if len(excludeList) == len(points[self.pointId].distinctEntries):
        #    return self.querySize

        # compute return
        newSampleSize = self.sampleSize + self.querySize
        n = self.sampleSize
        Kprime = self.estimateKprime(newSampleSize)
        f1c = self.estimateAlteredSingletons()
        f1 = self.freqCounters[1]
        newItems = (K*f1/n - Kprime*(f1 - f1c)/newSampleSize)/(1.0 + Kprime/newSampleSize)
        return newItems, K

    # normalized return
    def normalizedReturn(self):
        return self.estimateReturn()/float(self.querySize)

    # cost of estimator
    def computeCost(self,maxQuerySize,maxExListSize):
        pointSpecificity = points[self.pointId].totalAssignedValues

        w_Q_Size = 1.0
        Q_value = float(self.querySize)/float(maxQuerySize)

        w_E_Size = 10.0
        E_value = float(self.excludeListSize)/float(maxExListSize)

        w_Spec = 1.0
        S_value = float(pointSpecificity)/3.0

        #cost = (w_Q_Size*Q_value + w_E_Size*E_value + S_value*w_Spec)/(w_Q_Size + w_E_Size + w_Spec)
        cost = w_Q_Size*Q_value + w_E_Size*E_value + S_value*w_Spec
        return cost

    # break excludelist to children
    def excludeListToChildren(self,excludeList):
        childrenExcludeLists = {}
        for d in points[self.pointId].descendants:
            childrenExcludeLists[d] = []
            for item in excludeList:
                if d.containsItem(item):
                    childrenExcludeLists[d].append(item)
        return childrenExcludeLists

    def querySizeToChildren(self):
        childrenQuerySizes = {}
        totalWeight = points[self.pointId].childrenTotalWeight()
        for d in points[self.pointId].descendants:
            querySize = float(self.querySize)*points[self.pointId].childrenWeights[d]/totalWeight
            childrenQuerySizes[d] = querySize
        return childrenQuerySizes

    def estimateStratifiedReturn(self,excludeList):
        gain = 0.0
        totalWeight = points[self.pointId].childrenTotalWeight()
        for d in points[self.pointId].childrenWeights:
            childExList = []
            # compute child's exclude list
            for item in excludeList:
                if d.containsItem(item):
                    childExList.append(item)
            childQuerySize = int(round(float(self.querySize)*points[self.pointId].childrenWeights[d]/totalWeight))
            # instanciate new estimator
            childGainEst = PointEstimateNew(d,childQuerySize,childExList,self.estMethod)
            childGain = childGainEst.estimateReturn(False,True)
            gain += childGain
            childGainEst.clear()
            del childExList[:]
        return gain

    # history based methods

    def compute_K_History(self):

        # Iterate over sampling history to compute old K values
        for i in range(len(points[self.pointId].distinctEntryLogs)-1):
            distinctEntries = points[self.pointId].distinctEntryLogs[i]
            entryFreqs = points[self.pointId].entryFrequencyLogs[i]

            # construct excludeList
            excludeList = self.constructExcludeList(distinctEntries)

            # update freq counters
            self.updateFreqCounterSampleSize(excludeList,entryFreqs)

            # compute K
            f0, K = self.estimateF0_regression()
            self.oldKValues[self.sampleSize] = K
            self.oldK = K


    def bootstrapVariance(self, num_samples):
        # grap retrieved items from lattice point
        data = np.array(points[self.pointId].retrievedEntries)
        n = len(data)
        # generate bootstrapped samples
        idx = npr.randint(0, n, (num_samples, n))
        samples = data[idx]

        # initialize return estimates
        returnEstimates = []
        K_estimates = []
        K_samplesizes = []
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
            newReturn, newK = self.estimateReturnBootStrap(newDistinct, newEntryFreqs)
            returnEstimates.append(newReturn)
            if newK:
                K_estimates.append(newK)
                K_samplesizes.append(self.sampleSize)
                
            del newSample[:]
            newDistinct.clear()
            newEntryFreqs.clear()
        variance = np.var(np.array(returnEstimates))
        mean = np.mean(np.array(returnEstimates))
        meanK = np.mean(np.array(K_estimates))
        meanSS = int(round(np.mean(np.array(K_samplesizes))))
        mean = np.mean(np.array(returnEstimates))
        alpha = 0.05
        statList = np.sort(np.array(returnEstimates))
        lowerValue = statList[int((alpha/2.0)*num_samples)]
        upperValue = statList[int((1-alpha/2.0)*num_samples)]
        return lowerValue, upperValue, mean, variance, meanK, meanSS

    def bootstrapVarianceAlt(self, num_samples):
        returnEstimates = []

        # for num_samples times, iterate over old samples for lattice point and estimate old K values
        for i in range(num_samples):
            # compute old K values
            self.oldKValues.clear()
            self.oldK = None
            excludeList = []
            lenDistinct = 0.0
            for s in points[self.pointId].sampleLogs:
                # get sample
                data = np.array(s)
                n = len(data)
                # generate bootstrapped samples
                idx = npr.randint(0, n, (1, n))
                newSample = data[idx]
                newEntryFreqs = {}

                # distinct entries
                distinctEntries = set(newSample)

                # update entry frequencies
                for id in newSample:
                    if id not in newEntryFreqs:
                        newEntryFreqs[id] = 1
                    else:
                        newEntryFreqs[id] += 1

                # construct exclude list
                excludeList = self.constructExcludeList(distinctEntries)
                lenDistinct = len(distinctEntries)
                if len(excludeList) == len(distinctEntries):
                    continue

                self.updateFreqCounterSampleSize(excludeList,newEntryFreqs)

                if self.sampleSize == 0.0:
                    continue

                # compute K
                f0, K = self.estimateF0_regression()
                self.oldKValues[self.sampleSize] = K
                self.oldK = K

                # clear dics
                newEntryFreqs.clear()
                distinctEntries.clear()
                del newSample[:]

            # compute return

            # check if exclude list contains the entire sample
            if len(excludeList) == lenDistinct:
                returnEstimates.append(self.querySize)

            elif self.sampleSize == 0.0:
                if points[self.pointId].emptyPopulation == True:
                    returnEstimates.append(0.0)
                else:
                    returnEstimates.append(self.querySize)

            else:
                newSampleSize = self.sampleSize + self.querySize
                n = self.sampleSize
                Kprime = self.estimateKprime(newSampleSize)
                f1c = self.estimateAlteredSingletons()
                f1 = self.freqCounters[1]
                newItems = (self.oldK*f1/n - Kprime*(f1 - f1c)/newSampleSize)/(1.0 + Kprime/newSampleSize)
                returnEstimates.append(newItems)

        # compute mean, upper,lower, variance
        variance = np.var(np.array(returnEstimates))
        mean = np.mean(np.array(returnEstimates))
        alpha = 0.05
        statList = np.sort(np.array(returnEstimates))
        lowerValue = statList[int((alpha/2.0)*num_samples)]
        upperValue = statList[int((1-alpha/2.0)*num_samples)]
        return lowerValue, upperValue, mean, variance



    # take action
    def takeAction(self):

        # construct excludeList
        excludeList = self.constructExcludeList(points[self.pointId].distinctEntries)

        # store old unique
        oldUnique = len(points[self.pointId].distinctEntries)

        # retrieve sample from underlying node
        s = points[self.pointId].retrieveSample(self.querySize, excludeList)

        # store new unique
        newUnique = len(points[self.pointId].distinctEntries)

        # compute gain
        gain = newUnique - oldUnique

        # update selected times
        self.timesSelected += 1.0

        return gain

    def estimateGain(self,upper=False):
        gain = self.estimateReturn()
        upperValue = gain
        lowerValue = gain
        if upper and len(points[self.pointId].retrievedEntries) > 0.0:
            lowerValue, upperValue, gain, variance = self.bootstrapVarianceAlt(100)
        else:
            variance = 0.0
        return gain, variance, upperValue, lowerValue


    def computeExactGain(self):
        sample = self.prepareAction()
        sampleSet = set(sample)
        gain = len(sampleSet.difference(points[self.pointId].distinctEntries))
        return gain,sample

    # prepare action
    def prepareAction(self):
        excludeList = self.constructExcludeList(points[self.pointId].distinctEntries)
        s = points[self.pointId].retrieveSamplePreempt(self.querySize,excludeList)
        return s

    def takeActionFinal(self,sample):
        # store old unique
        oldUnique = len(points[self.pointId].distinctEntries)

        # update lattice sample based on sample
        points[self.pointId].finalizeSample(sample)

        # store new unique
        newUnique = len(points[self.pointId].distinctEntries)
        # compute gain
        gain = newUnique - oldUnique
        return gain