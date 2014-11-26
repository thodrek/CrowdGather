__author__ = 'thodoris'
from utilities import LatticePoint,DBManager

db = DBManager.DBManager()
hDescr = ['category','time','location']
newpoint = LatticePoint.LatticePoint('||', db, hDescr, None, samplingHistory=False)

points = {}
points['root'] = newpoint