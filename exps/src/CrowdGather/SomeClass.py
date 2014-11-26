from multiprocessing import Pool
import PointEstimateShenTest
import math


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
        pool = Pool(processes=3)
        results = pool.map(self.f,s)
        return results

    def run(self):
        s = []
        for i in range(10):
            for j in range(10):
                newS = PointEstimateShenTest.PointEstimateShenTest("root"",i,j,"shenRegression")
                s.append((newS,1.0,10,10))
        return self.go(s)
