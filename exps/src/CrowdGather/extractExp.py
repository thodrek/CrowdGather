__author__ = 'thodoris'

import EntityExtraction
import cPickle as pickle

# construct hierarchy list
catH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/categoryHierarchy.pkl","rb"))
timeH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/timeHierarchy.pkl","rb"))
locH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/locHierarchy.pkl","rb"))
hList = [catH,timeH,locH]

# construct hierarchy descr
hDescr = ['category','time','location']

# construct item info
itemInfo = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/eventBriteInfo.pkl","rb"))

# set budget
budget = 100

# set query configurations
configurations = [(5,0),(10,0),(20,0),(50,0),(100,0),(5,2),(10,2),(10,5),(20,2),(20,5),(20,10),(50,2),(50,5),(50,10),(50,20),(100,2),(100,5),(100,10),(100,20),(100,50)]
#configurations = [(10,5)]
# initialize new EntityExtraction

eExtract = EntityExtraction.EntityExtraction(budget,hList,hDescr,itemInfo,configurations,100,50,"GS_thres","chao92",lattice)

gain, cost = eExtract.retrieveItems()

print "Gain = ",gain
print "Cost = ",cost