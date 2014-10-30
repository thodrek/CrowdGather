__author__ = 'thodrek'
import cPickle as pickle
from utilities import Lattice

catH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/categoryHierarchy.pkl","rb"))
timeH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/timeHierarchy.pkl","rb"))
locH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/locHierarchy.pkl","rb"))

hDescr = ['location','category','time']

newLattice = Lattice.Lattice([catH,timeH,locH],hDescr)

