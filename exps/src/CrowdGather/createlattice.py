__author__ = 'thodrek'
import cPickle as pickle
from utilities import Lattice

catH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/categoryHierarchy.pkl","rb"))
timeH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/timeHierarchy.pkl","rb"))
locH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/locHierarchy.pkl","rb"))
itemInfo = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/eventBriteInfo.pkl","rb"))
hDescr = ['category','time','location']

newLattice = Lattice.Lattice([catH,timeH,locH],hDescr,itemInfo)

emptyPoints = []
counter = 0
for p in newLattice.points:
    po = newLattice.points[p]
    if len(po.db.getKeySET(p)) > 10.0 and po.totalAssignedValues == 2:
        emptyPoints.append(p)
        counter += 1
    if counter > 5:
        break


p = newLattice.points[emptyPoints[0]]
s = p.retrieveSample(5)
root = newLattice.points['||']
p.propagateSample(s)


import PointEstimateShen
import PointEstimateNew
root = newLattice.points['||']

est = PointEstimateShen.PointEstimateShen(root,10,0)
estNew = PointEstimateNew.PointEstimateNew(root,10,0)

r1 = est.estimateReturn()
r2 = est.estimateReturn("shenRegression")
r3 = estNew.estimateReturn()

print r1, r2, r3

root.retrieveSample(10,[])

r1 = est.estimateReturn()
r2 = est.estimateReturn("shenRegression")
r3 = estNew.estimateReturn()

print r1, r2, r3

oldE = len(root.distinctEntries)
excList = estNew.constructExcludeList()
x = root.retrieveSample(10,excList)
newE = len(root.distinctEntries)
actualReturn = newE - oldE
print actualReturn

r1 = est.estimateReturn()
r2 = est.estimateReturn("shenRegression")
r3 = estNew.estimateReturn()

print r1, r2, r3


