__author__ = 'thodoris'


import cPickle as pickle
from utilities import Lattice
import PointEstimateShen
import PointEstimateNew

catH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/categoryHierarchy.pkl","rb"))
timeH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/timeHierarchy.pkl","rb"))
locH = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/locHierarchy.pkl","rb"))
itemInfo = pickle.load(open("/scratch0/Dropbox/Eventbrite/eventsHierarchies/eventBriteInfo.pkl","rb"))
hDescr = ['category','time','location']

newLattice = Lattice.Lattice([catH,timeH,locH],hDescr,itemInfo)

# grab sample points
samplePoints = []
counter = 0
for p in newLattice.points:
    po = newLattice.points[p]
    if len(po.db.getKeySET(p)) > 500.0:
        samplePoints.append(po)
        counter += 1
    if counter > 10:
        break

# configurations (querySize, excludeListSize)
#configurations = [(5,0),(10,0),(20,0),(50,0),(100,0),(5,2),(10,2),(10,5),(20,2),(20,5),(20,10),(50,2),(50,5),(50,10),(50,20),(100,2),(100,5),(100,10),(100,20),(100,50)]
configurations = [(5,0)]
samples = 10
errors = {}

print 'Computing Errors...',
for conf in configurations:
    errors[conf] = {}
    errors[conf]['chao'] = []
    errors[conf]['regr'] = []
    errors[conf]['new'] = []
    querySize = conf[0]
    excludeListSize = conf[1]
    # for each point in samplePoints create estimators
    for p in samplePoints:
        est = PointEstimateShen.PointEstimateShen(p,querySize,excludeListSize)
        estNew = PointEstimateNew.PointEstimateNew(p,querySize,excludeListSize)
        totalErrorChao = 0.0
        totalErrorRegr = 0.0
        totalErrorNew = 0.0
        # retrieve samples
        for i in range(1,samples+1):

            # newUnique
            oldUnique = len(p.distinctEntries)

            # estimates
            estChao = est.estimateReturn()
            estRegr = est.estimateReturn("shenRegression")
            estNewRegr = estNew.estimateReturn()

            # excludeList
            exList = estNew.constructExcludeList()

            # retrievesample
            p.retrieveSample(querySize,exList)

            # new Unique
            newUnique = len(p.distinctEntries)
            actualReturn = newUnique - oldUnique

            # errors
            print p.key, querySize,excludeListSize, i, actualReturn,estChao,estRegr, estNewRegr
            totalErrorChao += abs(estChao - actualReturn)/float(actualReturn+1.0)
            totalErrorRegr += abs(estRegr - actualReturn)/float(actualReturn+1.0)
            totalErrorNew += abs(estNewRegr - actualReturn)/float(actualReturn+1.0)

        # avg error
        avgErrorChao = totalErrorChao/float(samples)
        avgErrorRegr = totalErrorRegr/float(samples)
        avgErrorNew = totalErrorNew/float(samples)

        # store errros
        errors[conf]['chao'].append(avgErrorChao)
        errors[conf]['regr'].append(avgErrorRegr)
        errors[conf]['new'].append(avgErrorNew)

        # reset point
        p.clearSampledPopulation()
print 'DONE.'

print 'Printing output file...',
# print output to csv
fileOut = open("estError.txt",'w')
header = "querySize\texListSize\tchao\tregr\tnew\n"
fileOut.write(header)
for conf in errors:
    querySize = conf[0]
    exListSize = conf[1]
    chaoAvg = sum(errors[conf]['chao'])/float(len(errors[conf]['chao']))
    regrAvg = sum(errors[conf]['regr'])/float(len(errors[conf]['regr']))
    newAvg = sum(errors[conf]['new'])/float(len(errors[conf]['new']))
    line = str(querySize)+"\t"+str(exListSize)+"\t"+str(chaoAvg)+"\t"+str(regrAvg)+"\t"+str(newAvg)+"\n"
    fileOut.write(line)
fileOut.close()
print 'DONE.'

