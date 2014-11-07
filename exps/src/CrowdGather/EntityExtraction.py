__author__ = 'thodoris'

import cPickle as pickle
from utilities import Lattice
import PointEstimateShen
import PointEstimateNew
import sys
import random
from Queue import PriorityQueue

class EntityExtraction:

    def __init__(self, budget, hList, hDescr, itemInfo, extConfigs, maxQuerySize, maxExListSize, optMethod, estMethod, lattice=None):
        # store budget
        self.budget = budget

        # generate latice
        if lattice:
            self.lattice = lattice
        else:
            self.lattice = Lattice.Lattice(hList,hDescr,itemInfo)

        # store extraction configurations
        self.extConfigs = extConfigs

        # maxQuerySize, maxExListSize
        self.maxQuerySize = maxQuerySize
        self.maxExListSize = maxExListSize

        # store extraction method
        if optMethod in ["random", "BFS", "GS_thres", "randomLeaves", "UCBFront"]:
            self.optMethod = optMethod
        else:
            print "Invalid extraction method specified"
            sys.exit(-1)

        # store estimation method
        if estMethod in ["chao92", "shenRegression", "newRegr"]:
            self.estMethod = estMethod
        else:
            print "Invalid estimation method specified"
            sys.exit(-1)



    def retrieveItems(self):
        if self.optMethod == "random":
            gain, cost = self.randomExtraction()
        elif self.optMethod == "BFS":
            gain, cost = self.bfsExtraction()
        elif self.optMethod == "GS_thres":
            gain, cost = self.graphSearchExtraction()
        elif self.optMethod == "randomLeaves":
            gain, cost = self.randomLeavesExtraction()
        else:
            gain, cost = self.ucbFrontierExtraction()
        return gain, cost

    def getNewEstimator(self, latticePoint, querySize, exListSize):
        if self.estMethod == "chao92" or self.estMethod == "shenRegression":
            return PointEstimateShen.PointEstimateShen(latticePoint,querySize,exListSize,self.estMethod)
        else:
            return PointEstimateNew.PointEstimateNew(latticePoint,querySize,exListSize)

    def randomExtraction(self):

        # keep track of queried nodex/configs
        previousQueries = {}

        cost = 0.0
        gain = 0.0

        while cost < self.budget:
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
            cost += est.computeCost(self.maxQuerySize,self.maxExListSize)
        return gain, cost

    def randomLeavesExtraction(self):

        # find leaf nodes
        leafKeys = []
        for pKey in self.lattice.points:
            if len(self.lattice.points[pKey].getDescendants()) == 0:
                leafKeys.append(pKey)

        # keep track of queried nodex/configs
        previousQueries = {}

        cost = 0.0
        gain = 0.0

        while cost < self.budget:
            # pick a node at random, pick a configuration at random and query it
            randomNode = random.choice(leafKeys)
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
            cost += est.computeCost(self.maxQuerySize,self.maxExListSize)
        return gain, cost

    def bfsExtraction(self):
        # traverse lattice in a BFS manner ask single query at each node using a random configuration
        # keep track of queried nodex/configs

        root = self.lattice.points['||']
        frontier = [root]
        activeNodes = {}
        activeNodes[root] = 1

        gain = 0.0
        cost = 0.0

        while cost < self.budget:
            # take the first point key in the frontier
            p = frontier.pop(0)

            # pick a random configuration
            randomConfig = random.choice(self.extConfigs)

            querySize = randomConfig[0]
            exListSize = randomConfig[1]

            # Retrieve estimator
            est = self.getNewEstimator(p,querySize,exListSize)

            gain += est.takeAction()
            cost += est.computeCost(self.maxQuerySize,self.maxExListSize)

            # Populate list with descendants of point
            for d in p.getDescendants():
                if d not in activeNodes:
                    frontier.append(d)
                    activeNodes[d] = 1

        return gain, cost

    # auxiliary functions
    def gsFindBestAction(self,frontier,nodeEstimates):
        bestAction = None
        bestScore = 0.0
        for node in frontier:
            for e in nodeEstimates[node]:
                # check if expected return is above a threshold
                cost = e.computeCost(self.maxQuerySize,self.maxExListSize)
                upperGain, gain, var = e.estimateGain(True)
                normGain = upperGain#/float(e.querySize)
                gainCostRatio = float(normGain)/float(cost)
                if gainCostRatio > bestScore:
                    bestAction = e
                    bestScore = gainCostRatio
        return bestAction, bestScore

    def graphSearchExtraction(self):
        # traverse lattice starting from root and based on previously
        # chosen decisions

        gain = 0.0
        cost = 0.0

        root = self.lattice.points['||']
        nodeEstimates = {}
        nodeEstimates[root] = []
        for conf in self.extConfigs:
            querySize = conf[0]
            exListSize = conf[1]
            est = self.getNewEstimator(root,querySize,exListSize)
            nodeEstimates[root].append(est)

        # initialize frontier
        frontier = set([root])


        while cost < self.budget:
            print "Running cost = ",cost
            print "Running gain = ",gain
            # pick the best configuration with expected return more than a threshold
            bestAction, bestScore = self.gsFindBestAction(frontier, nodeEstimates)
            if bestAction:
                gain += bestAction.takeAction()
                cost += bestAction.computeCost(self.maxQuerySize,self.maxExListSize)
            else:
                print "No good action found."
                sys.exit(-1)

            # Extend action collection -- for the current node extract the estimates for each children
            for d in bestAction.point.getDescendants():
                if d not in nodeEstimates:
                    nodeEstimates[d] = []
                    for conf in self.extConfigs:
                        querySize = conf[0]
                        exListSize = conf[1]
                        est = self.getNewEstimator(d,querySize,exListSize)
                        nodeEstimates[d].append(est)

            # check if node corresponding to bestAction should be removed from queue
            bestChildAction, bestChildScore = self.gsFindBestAction(set([bestAction.point.getDescendants]),nodeEstimates)
            bestNodeAction, bestNodeScore = self.gsFindBestAction(set([bestAction.point]),nodeEstimates)

            if bestNodeScore <= bestChildScore:
                frontier |= set(bestAction.point.getDescendants)
                frontier.discard(bestAction.point)

        return gain, cost