__author__ = 'thodoris'

import EntityExtractionParallel
import cPickle as pickle
import sys
from utilities import LatticePoint,DBManager

import copy_reg
import types
import math

def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    if isinstance(cls, type):
        # handle classmethods differently
        cls = obj
        obj = None
    if func_name.startswith('__') and not func_name.endswith('__'): #deal with mangled names
        cls_name = cls.__name__.lstrip('_')
        func_name = '_' + cls_name + func_name
    return _unpickle_method, (func_name, obj, cls)


def _pickle_method(method):
     func_name = method.im_func.__name__
     obj = method.im_self
     cls = method.im_class
     return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
    for cls in cls.__mro__:
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)

copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)


if __name__ == "__main__":
    #extractionMethods = ["random", "BFS", "GS_thres", "randomLeaves"]
    # estimator = ["chao92", "shenRegression", "newRegr"]
    #extractionMethods = ["BFS","GS_thres"]
    extractionMethods = ["GS_thres"]
    estimator = ["chao92","shenRegression","newRegr"]
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
    db = DBManager.DBManager()
    newLatticePoint = LatticePoint.LatticePoint('||', db, hDescr, None, samplingHistory=False)

    # set budget
    budget = int(sys.argv[1])

    # set query configurations
    #configurations = [(5,0),(10,0),(20,0),(50,0),(100,0),(5,2),(10,2),(10,5),(20,2),(20,5),(20,10),(50,2),(50,5),(50,10),(50,20),(100,2),(100,5),(100,10),(100,20),(100,50)]
    configurations = [(5,0),(10,0),(20,0),(5,2),(10,5),(20,5),(20,10)]
    #configurations = [(10,5)]
    # initialize new EntityExtraction
    newLattice = None
    lines = []

    eExtract = EntityExtractionParallel.EntityExtractionParallel(budget,hList,hDescr,itemInfo,configurations,20,10,extractionMethods[0],estimator[0],newLattice)
    print eExtract.graphSearchExtractionTest(newLatticePoint)
