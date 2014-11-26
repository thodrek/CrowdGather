from pathos.pp import ParallelPythonPool as Pool
import PointEstimateShen
import math
from utilities import LatticePoint,DBManager

db = DBManager.DBManager()
hDescr = ['category','time','location']
newLatticePoint = LatticePoint.LatticePoint('||', db, hDescr, None, samplingHistory=False)

class someClass(object):

    def __init__(self):
        pass

    def f(self, args):
        #can put something expensive here to verify CPU utilization
        e, round, mQ, mL = args
        cost = e.computeCost(mQ,mL)
        gain, variance, upperGain, lowerGain = e.estimateGain(True)
        armGain = gain + math.sqrt(variance*math.log(round)/e.timesSelected)
        gainCostRatio = float(armGain)/float(cost)
        return gainCostRatio
 
    def go(self,s):
        pool = Pool()
        results = pool.map(self.f,s)
        return results

    def run(self):
        s = []
        for i in range(10):
            for j in range(10):
                newS = PointEstimateShen.PointEstimateShen(None,i,j,"shenRegression")
                s.append((newS,1.0,10,10))
        return self.go(s)
