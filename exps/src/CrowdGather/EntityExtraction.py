__author__ = 'thodoris'

import cPickle as pickle
from utilities import Lattice
import PointEstimateShen
import PointEstimateNew
import sys
import random

class EntityExtraction:

    def __init__(self, budget, hList, hDescr, itemInfo, extConfigs, optMethod, estMethod):
        # store budget
        self.budget = budget

        # generate latice
        self.lattice = Lattice.Lattice(hList,hDescr,itemInfo)

        # store extraction configurations
        self.extConfigs = extConfigs

        # store extraction method
        if optMethod in ["random", "BFS", "randomLeaves", "UCBFront"]:
            self.optMethod = optMethod
        else:
            print "Invalid extraction method specified"
            sys.exit(-1)

        # store estimation method
        if estMethod in ["chao92", "shenRegression", "newRegr"]:
            self.estMathod = estMethod
        else:
            print "Invalid estimation method specified"
            sys.exit(-1)



    def retrieveItems(self):
        if self.optMethod == "random":
            gain, cost = self.randomExtraction()
        elif self.optMethod == "BFS":
            gain, cost = self.bfsExtraction()
        elif self.optMethod == "randomLeaves":
            gain, cost = self.randomLeavesExtraction()
        else:
            gain, cost = self.ucbFrontierExtraction()
        return gain, cost

    def getNewEstimator(self, latticePoint, querySize, exListSize):
        if self.estMethod == "chao92" or self.estMethod == "shenRegression":
            return PointEstimateShen.PointEstimateShen(latticePoint,querySize,exListSize,self.estMathod)
        else:
            return PointEstimateNew.PointEstimateNew(latticePoint,querySize,exListSize)

    def randomExtraction(self):

        # keep track of queried nodex/configs
        previousQueries = {}

        cost = 0.0
        gain = 0.0

        while cost <= self.budget:
            # pick a node at random, pick a configuration at random and query it
            randomNode = random.choice(self.lattice.points.keys())
            randomConfig = random.choice(self.extConfigs)

            querySize = randomConfig[0]
            exListSize = randomConfig[1]

            # form action key and retrieve estimator
            queryKey = (randomNode,querySize,exListSize)
            if queryKey not in previousQueries:
                est = self.getNewEstimator(self.lattice.points[randomNode],querySize,exListSize)
                previousQueries[queryKey] = est
            else:
                est = previousQueries[queryKey]

            gain += est.takeAction()
            cost += 1.0
        return gain, cost

