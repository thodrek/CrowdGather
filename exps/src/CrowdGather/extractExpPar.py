__author__ = 'thodoris'

import EntityExtractionParallel
import cPickle as pickle
import sys
from utilities import Lattice
import inputData

if __name__ == "__main__":
    #extractionMethods = ["random", "BFS", "GS_thres", "randomLeaves"]
    # estimator = ["chao92", "shenRegression", "newRegr"]
    #extractionMethods = ["BFS","GS_thres"]
    extractionMethods = ["GS_thres"]
    estimator = ["chao92","shenRegression","newRegr"]

    # set budget
    budget = int(sys.argv[1])

    # set query configurations
    #configurations = [(5,0),(10,0),(20,0),(50,0),(100,0),(5,2),(10,2),(10,5),(20,2),(20,5),(20,10),(50,2),(50,5),(50,10),(50,20),(100,2),(100,5),(100,10),(100,20),(100,50)]
    configurations = [(5,0),(10,0),(20,0),(5,2),(10,5),(20,5),(20,10)]
    #configurations = [(10,5)]
    # initialize new EntityExtraction

    lines = []

    for eMethod in extractionMethods:
        for est in estimator:
            eExtract = EntityExtractionParallel.EntityExtractionParallel(budget,configurations,20,10,eMethod,est)
            gain, cost = eExtract.retrieveItems()
            print "EstMethod, est, Gain, cost",eMethod,est,gain,cost
            newLine = str(eMethod) +"\t"+ str(est)+"\t"+str(gain)+"\t"+str(cost)+"\n"
            lines.append(newLine)
            inputData.newLattice.clearLatticeSamples()

    # print lines
    fileOut = open("extractionPerfNewPar.txt",'w')
    for l in lines:
        fileOut.write(l)
    fileOut.close()