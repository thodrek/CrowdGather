__author__ = 'thodoris'

import EntityExtraction
import cPickle as pickle
import numpy
from utilities import Lattice
import math

if __name__ == "__main__":
    extractionMethods = ["random", "randomLeaves", "BFS", "GS_thres", "GS_exact"]
    estimator = ["chao92", "shenRegression", "newRegr"]
    #extractionMethods = ["BFS","GS_thres"]
    #extractionMethods = ["GS_thres"]
    #estimator = ["newRegr"]
    # construct hierarchy list
    typeH = pickle.load(open("/Users/thodoris/Desktop/crowdData/ptypeHierarchy.pkl","rb"))
    newspH = pickle.load(open("/Users/thodoris/Desktop/crowdData/newspaperHierarchy.pkl","rb"))
    hList = [typeH,newspH]

    # construct hierarchy descr
    hDescr = ['type','paper']

    # construct item info
    itemInfo = pickle.load(open("/Users/thodoris/Desktop/crowdData/peopleInfo.pkl","rb"))

    # create lattice
    newLattice = Lattice.Lattice(hList,hDescr,itemInfo)

    # set budget
    budgetValues = [10,20,50,80,100]
    #budgetValues = [20,50]

    # set query configurations
    #configurations = [(5,0),(10,0),(20,0),(50,0),(100,0),(5,2),(10,2),(10,5),(20,2),(20,5),(20,10),(50,2),(50,5),(50,10),(50,20),(100,2),(100,5),(100,10),(100,20),(100,50)]
    configurations = [(5,0),(10,0),(20,0),(5,2),(10,5),(20,5),(20,10)]
    #configurations = [(10,5)]
    # initialize new EntityExtraction

    # initialize action log
    actionLog = {}
    for c in configurations:
        cKey = str(c[0])+"_"+str(c[1])
        actionLog[cKey] = {}
        for i in range(3):
            actionLog[cKey][i] = []

    fileName = "linearCost_Variance_Mean_Round_Real/extPerformance_budget.txt"
    fileOut = open(fileName,'w')
    for b in budgetValues:
        newLine = str(b)
        print "Starting exps with budget ",b
        for eMethod in extractionMethods:
            print "Starting exps with method ",eMethod

            if eMethod in ["random", "randomLeaves", "BFS"]:
                gainValues = []
                costValues = []
                for i in range(10):
                    eExtract = EntityExtraction.EntityExtraction(b,hList,hDescr,itemInfo,configurations,20,10,eMethod,"chao92",newLattice)
                    gain, cost, actionsSelected = eExtract.retrieveItems()
                    gainValues.append(gain)
                    costValues.append(cost)
                    newLattice.clearLatticeSamples()

                # compute mean - variance
                gainMean = numpy.mean(gainValues)
                gainVar = numpy.var(gainValues)
                gainSTE = math.sqrt(gainVar/10.0)
                costMean = numpy.mean(costValues)
                costVar = numpy.var(costValues)
                newLine += "\t" + str(gainMean) + "\t" + str(gainSTE)
                #newLine = str(eMethod)+"\t"+"\t"+str(gainMean)+"\t"+str(gainVar)+"\t"+str(costMean)+"\t"+str(costVar)+"\n"
                #fileOut.write(newLine)
            elif eMethod == "GS_exact":

                fileNameActions = "linearCost_Variance_Mean_Round_Real/actionsTaken_"+str(b)+"_Exact.txt"
                fileOutActions = open(fileNameActions,'w')

                # clean action log
                for c in configurations:
                    cKey = str(c[0])+"_"+str(c[1])
                    for i in range(3):
                        del actionLog[cKey][i][:]
                gainValues = []
                costValues = []
                for i in range(5):
                    eExtract = EntityExtraction.EntityExtraction(b,hList,hDescr,itemInfo,configurations,20,10,eMethod,"chao92",newLattice)
                    gain, cost, actionsSelected = eExtract.retrieveItems()
                    gainValues.append(gain)
                    costValues.append(cost)
                    #print "EstMethod, est, Gain, cost",eMethod,est,gain,cost
                    newLattice.clearLatticeSamples()

                    for a in actionsSelected:
                        for level in actionsSelected[a]:
                            actionLog[a][level].append(actionsSelected[a][level])

                gainMean = numpy.mean(gainValues)
                gainVar = numpy.var(gainValues)
                gainSTE = math.sqrt(gainVar/5.0)
                costMean = numpy.mean(costValues)
                costVar = numpy.var(costValues)
                newLine += "\t" + str(gainMean) + "\t" + str(gainSTE)

                # compute average actions selected
                for cKey in actionLog:
                    newActionLine = cKey
                    for l in actionLog[cKey]:
                        # average times action taken
                        if len(actionLog[cKey][l]) == 0:
                            avrgSelected = 0
                        else:
                            avrgSelected = numpy.mean(actionLog[cKey][l])
                        newActionLine += "\t" + str(l) + "\t" + str(avrgSelected)
                    newActionLine += "\n"
                    fileOutActions.write(newActionLine)
                fileOutActions.close()
                #newLine = str(eMethod) +"\t"+ str(est)+"\t"+str(gainMean)+"\t"+str(gainVar)+"\t"+str(costMean)+"\t"+str(costVar)+"\n"
                #fileOut.write(newLine)
            else:
                for est in estimator:
                    gainValues = []
                    costValues = []
                    fileNameActions = "linearCost_Variance_Mean_Round_Real/actionsTaken_"+str(b)+"_GS+"+est+".txt"
                    fileOutActions = open(fileNameActions,'w')

                    # clean action log
                    for c in configurations:
                        cKey = str(c[0])+"_"+str(c[1])
                        for i in range(3):
                            del actionLog[cKey][i][:]
                    for i in range(5):
                        eExtract = EntityExtraction.EntityExtraction(b,hList,hDescr,itemInfo,configurations,20,10,eMethod,est,newLattice)
                        gain, cost, actionsSelected = eExtract.retrieveItems()
                        gainValues.append(gain)
                        costValues.append(cost)
                        #print "EstMethod, est, Gain, cost",eMethod,est,gain,cost
                        newLattice.clearLatticeSamples()

                        for a in actionsSelected:
                            for level in actionsSelected[a]:
                                actionLog[a][level].append(actionsSelected[a][level])

                    gainMean = numpy.mean(gainValues)
                    gainVar = numpy.var(gainValues)
                    gainSTE = math.sqrt(gainVar/5.0)
                    costMean = numpy.mean(costValues)
                    costVar = numpy.var(costValues)
                    newLine += "\t" + str(gainMean) + "\t" + str(gainSTE)
                    #newLine = str(eMethod) +"\t"+ str(est)+"\t"+str(gainMean)+"\t"+str(gainVar)+"\t"+str(costMean)+"\t"+str(costVar)+"\n"
                    #fileOut.write(newLine)

                    # compute average actions selected
                    for cKey in actionLog:
                        newActionLine = cKey
                        for l in actionLog[cKey]:
                            # average times action taken
                            if len(actionLog[cKey][l]) == 0:
                                avrgSelected = 0
                            else:
                                avrgSelected = numpy.mean(actionLog[cKey][l])
                            newActionLine += "\t" + str(l) + "\t" + str(avrgSelected)
                        newActionLine += "\n"
                        fileOutActions.write(newActionLine)
                    fileOutActions.close()

                    print "DONE with",eMethod," with estimator",est," with budget",b
            print "DONE with",eMethod," with budget",b
            newLine += "\n"
            fileOut.write(newLine)
    fileOut.close()