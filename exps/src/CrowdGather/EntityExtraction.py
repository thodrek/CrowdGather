__author__ = 'thodoris'

import cPickle as pickle
from utilities import Lattice
import PointEstimateShen
import PointEstimateNew
import sys
import random
import math

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
        if optMethod in ["random", "BFS", "GS_thres", "BerkBaseline", "GS_exact", "randomLeaves", "UCBFront", "GS_thres_NoEx"]:
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
            gain, cost, actionsSelected, gainHist, costHist = self.randomExtraction()
        elif self.optMethod == "BFS":
            gain, cost, actionsSelected, gainHist, costHist = self.bfsExtraction()
        elif self.optMethod == "GS_thres":
            gain, cost, actionsSelected, gainHist, costHist = self.graphSearchExtraction()
        elif self.optMethod == "GS_thres_NoEx":
            gain, cost, actionsSelected, gainHist, costHist = self.graphSearchExtraction(True)
        elif self.optMethod == "GS_exact":
            gain, cost, actionsSelected, gainHist, costHist = self.graphSearchExtractionExact()
        elif self.optMethod == "randomLeaves":
            gain, cost, actionsSelected, gainHist, costHist = self.randomLeavesExtraction()
        elif self.optMethod == "BerkBaseline":
            gain, cost, actionsSelected, gainHist, costHist = self.berkBaselinePlus()
        else:
            gain, cost, actionsSelected, gainHist, costHist = self.graphSearchExtractionExact()
        return gain, cost, actionsSelected, gainHist, costHist

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

        gainHist = []
        costHist = []

        gainHist.append(gain)
        costHist.append(cost)

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

            if (cost + est.computeCost(self.maxQuerySize,self.maxExListSize)) <= self.budget:
                gain += est.takeAction()
                cost += est.computeCost(self.maxQuerySize,self.maxExListSize)
                gainHist.append(gain)
                costHist.append(cost)
            else:
                break
        return gain, cost, None, gainHist, costHist

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

        gainHist = []
        costHist = []

        gainHist.append(gain)
        costHist.append(cost)

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

            if (cost + est.computeCost(self.maxQuerySize,self.maxExListSize)) <= self.budget:
                gain += est.takeAction()
                cost += est.computeCost(self.maxQuerySize,self.maxExListSize)
                gainHist.append(gain)
                costHist.append(cost)
            else:
                break
        return gain, cost, None, gainHist, costHist

    def bfsExtraction(self):
        # traverse lattice in a BFS manner ask single query at each node using a random configuration
        # keep track of queried nodex/configs

        root = self.lattice.points['||']
        frontier = [root]
        activeNodes = {}
        activeNodes[root] = 1

        gain = 0.0
        cost = 0.0

        gainHist = []
        costHist = []

        gainHist.append(gain)
        costHist.append(cost)

        while cost < self.budget and len(frontier) > 0:
            #print "Running cost,gain\t",cost,gain
            # take the first point key in the frontier
            p = frontier.pop(0)

            # pick a random configuration
            randomConfig = random.choice(self.extConfigs)

            querySize = randomConfig[0]
            exListSize = randomConfig[1]

            # Retrieve estimator
            est = self.getNewEstimator(p,querySize,exListSize)


            if (cost + est.computeCost(self.maxQuerySize,self.maxExListSize)) <= self.budget:
                actualGain = est.takeAction()
                gain += est.takeAction()
                cost += est.computeCost(self.maxQuerySize,self.maxExListSize)

                gainHist.append(gain)
                costHist.append(cost)

                #print "Took:", est.point.getKey(),"with qS:",est.querySize,"and exS:",est.excludeListSize
                #print "Actual gain was:", actualGain

                # Populate list with descendants of point
                for d in p.getDescendants():
                    if d not in activeNodes:
                        frontier.append(d)
                        activeNodes[d] = 1
            else:
                pass

        return gain, cost, None, gainHist, costHist

    def berkBaselinePlus(self):

        root = self.lattice.points['||']
        gain = 0.0
        cost = 0.0

        gainHist = []
        costHist = []

        gainHist.append(gain)
        costHist.append(cost)

        round = 1.0
        nodeEstimates = {}
        nodeEstimates[root] = []
        for conf in self.extConfigs:
            querySize = conf[0]
            exListSize = conf[1]
            est = self.getNewEstimator(root,querySize,exListSize)
            nodeEstimates[root].append(est)

        # initialize frontier
        frontier = set([root])

        # actions selected
        actionsSelected = {}

        while cost < self.budget:
            remBudget = self.budget - cost
            bestAction, bestScore, bestGain = self.gsFindBestAction(frontier, nodeEstimates, round, remBudget)
            if bestAction:
                actualGain = bestAction.takeAction()
                gain += actualGain
                #print "Took:", bestAction.point.getKey(),"with qS:",bestAction.querySize,"and exS:",bestAction.excludeListSize
                #print "Actual gain was:", actualGain
                #print "Predicted gain was:", bestGain
                #print "Gain so far ",gain
                cost += bestAction.computeCost(self.maxQuerySize,self.maxExListSize)

                gainHist.append(gain)
                costHist.append(cost)

                round += 1.0

                # log selected action
                bestActionConfig = str(bestAction.querySize)+"_"+str(bestAction.excludeListSize)
                bestActionLevel = bestAction.point.totalAssignedValues

                if bestActionConfig not in actionsSelected:
                    actionsSelected[bestActionConfig] = {}

                if bestActionLevel not in actionsSelected[bestActionConfig]:
                    actionsSelected[bestActionConfig][bestActionLevel] = 0

                actionsSelected[bestActionConfig][bestActionLevel] += 1

            else:
                break

        return gain, cost, actionsSelected, gainHist, costHist

    # auxiliary functions
    def gsFindBestAction(self,frontier,nodeEstimates,round,remBudget):
        bestAction = None
        bestScore = 0.0
        bestGain = 0.0
        for node in frontier:
            for e in nodeEstimates[node]:
                # check if expected return is above a threshold
                cost = e.computeCostStep(self.maxQuerySize,self.maxExListSize)
                if cost <= remBudget:
                    gain, variance, upperGain, lowerGain = e.estimateGain(True)
                    armGain = gain + math.sqrt(variance*math.log(round)/e.timesSelected)
                    #armGain = gain
                    gainCostRatio = float(armGain)/float(cost)
                    #gainCostRatio = float(armGain)
                    if gainCostRatio > bestScore:
                        bestAction = e
                        bestScore = gainCostRatio
                        bestGain = armGain
        return bestAction, bestScore, bestGain

    def graphSearchExtraction(self,noList = False):
        # traverse lattice starting from root and based on previously
        # chosen decisions

        gain = 0.0
        cost = 0.0


        gainHist = []
        costHist = []

        gainHist.append(gain)
        costHist.append(cost)

        round = 1.0

        # actions selected
        actionsSelected = {}

        root = self.lattice.points['||']
        nodeEstimates = {}
        removedNodes = set([])
        nodeEstimates[root] = []
        for conf in self.extConfigs:
            querySize = conf[0]
            exListSize = conf[1]
            if noList and exListSize != 0:
                pass
            else:
                est = self.getNewEstimator(root,querySize,exListSize)
                nodeEstimates[root].append(est)

        # initialize frontier
        frontier = set([root])


        while cost < self.budget:
            #print "Running cost,gain\t",cost,gain
            # pick the best configuration with expected return more than a threshold
            remBudget = self.budget - cost
            bestAction, bestScore, bestGain = self.gsFindBestAction(frontier, nodeEstimates,round,remBudget)
            if bestAction:
                actualGain = bestAction.takeAction()
                gain += actualGain
                #print "Took:", bestAction.point.getKey(),"with qS:",bestAction.querySize,"and exS:",bestAction.excludeListSize
                #print "Actual gain was:", actualGain
                #print "Predicted gain was:", bestGain
                #print "Gain so far ",gain
                cost += bestAction.computeCost(self.maxQuerySize,self.maxExListSize)

                gainHist.append(gain)
                costHist.append(cost)

                round += 1.0

                # log selected action
                bestActionConfig = str(bestAction.querySize)+"_"+str(bestAction.excludeListSize)
                bestActionLevel = bestAction.point.totalAssignedValues

                if bestActionConfig not in actionsSelected:
                    actionsSelected[bestActionConfig] = {}

                if bestActionLevel not in actionsSelected[bestActionConfig]:
                    actionsSelected[bestActionConfig][bestActionLevel] = 0

                actionsSelected[bestActionConfig][bestActionLevel] += 1

            else:
                break

            # Extend action collection -- for the current node extract the estimates for its children
            descSet = set([])
            for d in bestAction.point.getDescendants():
                if d not in removedNodes:
                    descSet.add(d)
                    if d not in nodeEstimates:
                        nodeEstimates[d] = []
                        for conf in self.extConfigs:
                            querySize = conf[0]
                            exListSize = conf[1]
                            if noList and exListSize != 0:
                                pass
                            else:
                                est = self.getNewEstimator(d,querySize,exListSize)
                                nodeEstimates[d].append(est)

            remBudget = self.budget - cost

            # check if node corresponding to bestAction should be removed from queue
            bestChildAction, bestChildScore, bestChildGain = self.gsFindBestAction(descSet,nodeEstimates,round,remBudget)
            bestNodeAction, bestNodeScore, bestNodeGain = self.gsFindBestAction(set([bestAction.point]),nodeEstimates,round,remBudget)

            if bestNodeScore < bestChildScore:
                frontier |= descSet
                frontier.discard(bestAction.point)
                removedNodes.add(bestAction.point)

        return gain, cost, actionsSelected, gainHist, costHist

    def gsFindBestActionExact(self,frontier,nodeEstimates, remBudget):
        bestAction = None
        bestScore = 0.0
        bestSample = []
        for node in frontier:
            for e in nodeEstimates[node]:
                # check if expected return is above a threshold
                cost = e.computeCost(self.maxQuerySize,self.maxExListSize)
                if cost <= remBudget:
                    gain, sample = e.computeExactGain()
                    normGain = gain
                    gainCostRatio = float(normGain)/float(cost)
                    if gainCostRatio > bestScore:
                        bestAction = e
                        bestScore = gainCostRatio
                        bestSample = sample
        return bestAction, bestScore, bestSample


    def graphSearchExtractionExact(self):
        # traverse lattice starting from root and based on previously
        # chosen decisions

        gain = 0.0
        cost = 0.0

        gainHist = []
        costHist = []

        gainHist.append(gain)
        costHist.append(cost)

        # actions selected
        actionsSelected = {}

        root = self.lattice.points['||']
        nodeEstimates = {}
        removedNodes = set([])
        nodeEstimates[root] = []
        for conf in self.extConfigs:
            querySize = conf[0]
            exListSize = conf[1]
            est = self.getNewEstimator(root,querySize,exListSize)
            nodeEstimates[root].append(est)

        # initialize frontier
        frontier = set([root])


        while cost < self.budget:
            #print "Running cost,gain\t",cost,gain
            # pick the best configuration with expected return more than a threshold
            remBudget = self.budget - cost
            bestAction, bestScore, bestSample = self.gsFindBestActionExact(frontier, nodeEstimates,remBudget)
            if bestAction:
                gain += bestAction.takeActionFinal(bestSample)
                cost += bestAction.computeCost(self.maxQuerySize,self.maxExListSize)

                gainHist.append(gain)
                costHist.append(cost)

                # log selected action
                bestActionConfig = str(bestAction.querySize)+"_"+str(bestAction.excludeListSize)
                bestActionLevel = bestAction.point.totalAssignedValues

                if bestActionConfig not in actionsSelected:
                    actionsSelected[bestActionConfig] = {}

                if bestActionLevel not in actionsSelected[bestActionConfig]:
                    actionsSelected[bestActionConfig][bestActionLevel] = 0

                actionsSelected[bestActionConfig][bestActionLevel] += 1

            else:
                break

            # Extend action collection -- for the current node extract the estimates for each children
            descSet = set([])
            for d in bestAction.point.getDescendants():
                if d not in removedNodes:
                    descSet.add(d)
                    if d not in nodeEstimates:
                        nodeEstimates[d] = []
                        for conf in self.extConfigs:
                            querySize = conf[0]
                            exListSize = conf[1]
                            est = self.getNewEstimator(d,querySize,exListSize)
                            nodeEstimates[d].append(est)

            remBudget = self.budget - cost

            # check if node corresponding to bestAction should be removed from queue
            bestChildAction, bestChildScore, bestSample = self.gsFindBestActionExact(descSet,nodeEstimates,remBudget)
            bestNodeAction, bestNodeScore, bestSample = self.gsFindBestActionExact(set([bestAction.point]),nodeEstimates,remBudget)

            if bestNodeScore <= bestChildScore:
                frontier |= descSet
                frontier.discard(bestAction.point)
                removedNodes.add(bestAction.point)


        return gain, cost, actionsSelected, gainHist, costHist
