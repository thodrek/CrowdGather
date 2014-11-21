__author__ = 'thodoris'

import EntityExtraction
import cPickle as pickle
import sys
from utilities import Lattice

def main(argv):

    #extractionMethods = ["random", "BFS", "GS_thres", "randomLeaves"]
    # estimator = ["chao92", "shenRegression", "newRegr"]
    extractionMethods = ["BFS","GS_exact","GS_thres"]
    estimator = ["chao92","newRegr",]
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
    budget = 10

    # set query configurations
    configurations = [(5,0),(10,0),(20,0),(50,0),(100,0),(5,2),(10,2),(10,5),(20,2),(20,5),(20,10),(50,2),(50,5),(50,10),(50,20),(100,2),(100,5),(100,10),(100,20),(100,50)]
    #configurations = [(10,5)]
    # initialize new EntityExtraction

    lines = []

    for eMethod in extractionMethods:
        for est in estimator:
            eExtract = EntityExtraction.EntityExtraction(budget,hList,hDescr,itemInfo,configurations,100,50,eMethod,est,newLattice)

            gain, cost = eExtract.retrieveItems()
            print "EstMethod, est, Gain, cost",eMethod,est,gain,cost
            newLine = str(eMethod) +"\t"+ str(est)+"\t"+str(gain)+"\t"+str(cost)+"\n"
            lines.append(newLine)
            newLattice.clearLatticeSamples()

    # print lines
    fileOut = open("extractionPerfNew.txt",'w')
    for l in lines:
        fileOut.write(l)
    fileOut.close()

if __name__ == "__main__":
    main(sys.argv)