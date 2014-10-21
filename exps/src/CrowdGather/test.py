__author__ = 'thodrek'

import YelpData
import NodeEstimate


yp = YelpData.YelpData()
hNode = yp.getBusHierarchy()['root']['Restaurants']['Greek']

yp_samplePoint = YelpData.YelpSample(yp,hNode,"review")

sp_estimate = NodeEstimate.Estimate(hNode,5,10)

# grab 5 samples
exList = sp_estimate.getExcludeList()
for i in range(5):
    #entries = yp_samplePoint.sampleKwithExList(exList,10)
    entries = yp_samplePoint.sampleK(10)
    sp_estimate.extendSample(entries)
    #exList = sp_estimate.getExcludeList()
oldK = 0.0
for i in range(6,20):
    entries = yp_samplePoint.sampleK(10)
    #entries = yp_samplePoint.sampleKwithExList(exList,10)
    oldUnique = sp_estimate.uniqueEntries()
    sp_estimate.extendSample(entries)
    #exList = sp_estimate.getExcludeList()
    w = 10.0*i/49.0
    q = 10.0*i/float(yp_samplePoint.totalPopulation())
    r = q/(1-q)
    f0, K = sp_estimate.estimateF0_regression(oldK)
    sp_estimate.storeOldK(i*10, K)
    print "\n\nNew sample. Printing unseen estimates"
    print "K regression = ", K
    print "F0 regression = ",f0
    print "F0 wo replacement (Chao 2012) = ", sp_estimate.estimateF0_wo_replacement(w,r)
    print "F0 Chao92 = ", sp_estimate.estimateF0_Chao92()
    print "F0 true = ", yp_samplePoint.totalPopulation()-sp_estimate.uniqueEntries()
    #print "Exclude list = ", exList

    print "\nPrinting new return estimates"
    print "Return regression =", sp_estimate.estimateReturn(10,"regression",oldK)
    print "Return Chao 12 =", sp_estimate.estimateReturn(10,"chao2012",w,r)
    print "Return Chao 92 =", sp_estimate.estimateReturn(10,"chao92")
    print "Return true = ", max(0.0,sp_estimate.uniqueEntries() - oldUnique)

    print "\nNew K estimate and new return"
    print "K_est = ", sp_estimate.estimateKprime((i)*10.0)
    print "K' = ", sp_estimate.estimateKprime((i+1)*10.0)
    print "Return new method = ", sp_estimate.estimateReturnNew(10,K)
    oldK = K
