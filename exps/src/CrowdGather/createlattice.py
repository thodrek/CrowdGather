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
    if len(po.db.getKeySET(p)) > 0.0 and po.totalAssignedValues == 2:
        emptyPoints.append(p)
        counter += 1
    if counter > 5:
        break