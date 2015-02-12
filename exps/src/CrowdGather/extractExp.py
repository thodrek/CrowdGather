__author__ = 'thodoris'

import EntityExtraction
import cPickle as pickle
import numpy
from utilities import Lattice

if __name__ == "__main__":
    #extractionMethods = ["random", "randomLeaves", "BFS", "GS_thres", "GS_thres_NoEx", "BerkBaseline"]
    estimator = ["chao92", "shenRegression", "newRegr"]
    #estimator = ["newRegr"]
    #extractionMethods = ["BFS","GS_thres"]
    #extractionMethods = ["BFS", "BerkBaseline", "GS_thres", "GS_thres_NoEx"]
    extractionMethods = ["BerkBaseline","GS_thres"]
    #extractionMethods = ["random", "randomLeaves", "BFS", "GS_thres", "BerkBaseline", "GS_exact"]
    #extractionMethods = ["GS_thres"]
    #estimator = ["chao92"]
    # construct hierarchy list
    catH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/categoryHierarchy.pkl","rb"))
    timeH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/timeHierarchy.pkl","rb"))
    locH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/locHierarchy.pkl","rb"))
    hList = [catH,timeH,locH]

    # construct hierarchy descr
    hDescr = ['category','time','location']

    # construct item info
    itemInfo = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/eventBriteInfo.pkl","rb"))

    # create lattice
    newLattice = Lattice.Lattice(hList,hDescr,itemInfo)

    # set budget
    budgetValues = [10,20,50,80,100]
    #budgetValues = [50,80,100]

    # set query configurations
    #configurations = [(5,0),(10,0),(20,0),(50,0),(100,0),(5,2),(10,2),(10,5),(20,2),(20,5),(20,10),(50,2),(50,5),(50,10),(50,20),(100,2),(100,5),(100,10),(100,20),(100,50)]
    configurations = [(5,0),(10,0),(20,0),(5,2),(10,5),(20,5),(20,10)]
    #configurations = [(10,5)]
    # initialize new EntityExtraction
    logOut = open("logTest.out",'w')
    for b in budgetValues:
        logLine = "Starting exps with budget "+str(b)+"\n"
        logOut.write(logLine)
        print "Starting exps with budget ",b
        fileName = "expPerformanceBerkGSThresKregr_Test_budget="+str(b)+".txt"
        fileOut = open(fileName,'w')
        for eMethod in extractionMethods:
            logLine = "Starting exps with method "+str(eMethod)+"\n"
            logOut.write(logLine)
            print "Starting exps with method ",eMethod
            if eMethod in ["random", "randomLeaves", "BFS", "BerkBaseline","GS_exact"]:
                gainValues = []
                costValues = []
                for i in range(5):
                    eExtract = EntityExtraction.EntityExtraction(b,hList,hDescr,itemInfo,configurations,20,10,eMethod,"chao92",newLattice)
                    gain, cost, actionSelected, gainHist, costHist = eExtract.retrieveItems()
                    gainValues.append(gain)
                    costValues.append(cost)
                    logLine = eMethod+"\t"+str(i)+"\t"+str(gain)+"\t"+str(cost)+"\t"+str(gainHist)+"\t"+str(costHist)+"\t"+str(actionSelected)+"\n"
                    logOut.write(logLine)
                    print eMethod, i, gain, cost, gainHist
                    newLattice.clearLatticeSamples()
                # compute mean - variance
                gainMean = numpy.mean(gainValues)
                gainVar = numpy.var(gainValues)

                costMean = numpy.mean(costValues)
                costVar = numpy.var(costValues)
                newLine = str(eMethod)+"\t"+"\t"+str(gainMean)+"\t"+str(gainVar)+"\t"+str(costMean)+"\t"+str(costVar)+"\n"
                print newLine
                logOut.write(newLine)
                fileOut.write(newLine)
            else:
                for est in estimator:
                    gainValues = []
                    costValues = []
                    for i in range(5):
                        eExtract = EntityExtraction.EntityExtraction(b,hList,hDescr,itemInfo,configurations,20,10,eMethod,est,newLattice)
                        gain, cost, actionSelected, gainHist, costHist = eExtract.retrieveItems()
                        gainValues.append(gain)
                        costValues.append(cost)
                        logLine = eMethod+"_"+str(est)+"\t"+str(i)+"\t"+str(gain)+"\t"+str(cost)+"\t"+str(gainHist)+"\t"+str(costHist)+"\t"+str(actionSelected)+"\n"
                        logOut.write(logLine)
                        print i, gain, cost, gainHist
                        newLattice.clearLatticeSamples()
                        #print "EstMethod, est, Gain, cost",eMethod,est,gain,cost
                        #newLattice.clearLatticeSamples()
                    # compute mean - variance
                    gainMean = numpy.mean(gainValues)
                    gainVar = numpy.var(gainValues)

                    costMean = numpy.mean(costValues)
                    costVar = numpy.var(costValues)
                    newLine = str(eMethod)+"_"+str(est)+"\t"+"\t"+str(gainMean)+"\t"+str(gainVar)+"\t"+str(costMean)+"\t"+str(costVar)+"\n"
                    fileOut.write(newLine)
                    logOut.write(newLine)
                    #newLine = str(eMethod) +"\t"+ str(est)+"\t"+str(gain)+"\t0.0"+"\t"+str(cost)+"\t0.0"+"\n"
                    #fileOut.write(newLine)
                    print newLine
                    print "DONE with",eMethod," with estimator",est," with budget",b
            print "DONE with",eMethod," with budget",b
        fileOut.close()