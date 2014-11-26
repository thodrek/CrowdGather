__author__ = 'thodoris'
import cPickle as pickle
from utilities import Lattice,LatticePoint,DBManager

db = DBManager.DBManager()
hDescr = ['category','time','location']
newpoint = LatticePoint.LatticePoint('||', db, hDescr, None, samplingHistory=False)


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

# global vars
lattice = newLattice
points = newLattice.points