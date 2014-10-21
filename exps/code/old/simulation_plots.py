import sys
import json
import random
import sets
import math
import numpy as np
import matplotlib.pyplot as plt

# Flatten dictionary to list of elements
def flatten_dict(d):
    for k,v in d.items():
        if isinstance(v, dict):
            for item in flatten_dict(v):
                yield item
        else:
            yield v

# Weighted Sampling without Replacement
def weightedSelectionWithoutReplacement(l, k):
    """Selects without replacement n random elements from a list of (weight, item) tuples."""
    l = sorted((random.random() * x[2], x[0]) for x in l)
    return l[-k:]

# Sample k-elements from underlying distribution
def sampleK(d,k):
    entryList = list(flatten_dict(d))
    sample = weightedSelectionWithoutReplacement(entryList,k)
    itemSample = list(x[1] for x in sample)
    return itemSample

# Sample k-elements from underlying distribution
def sampleKList(entryList,k):
    sample = weightedSelectionWithoutReplacement(entryList,k)
    itemSample = list(x[1] for x in sample)
    return itemSample

# Compute Chao1 estimator based on abundance data
def chao1Estimate(sample):
    
    # find element counts
    
    elementCounts = {}
    for e in sample:
        if e not in elementCounts:
            elementCounts[e] = 1.0
        else:
            elementCounts[e] += 1.0

    # compute Sobs, fValues
    Sobs = len(elementCounts)
    fValues = {}
    for e in elementCounts:
        if elementCounts[e] not in fValues:
            fValues[elementCounts[e]] = 1.0
        else:
            fValues[elementCounts[e]] += 1.0
        
    Schao1 = 0.0 
    Schao1Var = 0.0

    if 1.0 in fValues:
        f1 = fValues[1.0]
    else:
        f1 = 0.0
    if 2.0 in fValues:
        f2 = fValues[2.0]
    else:
        f2 = 0.0

    n = float(len(sample))
    
    if f1 > 0.0 and f2 > 0.0:
        Schao1 = Sobs + ((n-1)/n)*f1*(f1-1)/(2*(f2+1))
        Schao1Var = f1*(f1-1.0)/2 + f1*((2*f1-1)**2)/(4*((f2+1)**2)) + (f1**2)*f2*((f1-1)**2)/(4*((f2+1)**2))
    elif f1 > 1.0 and f2 == 0.0:
        Schao1 = Sobs + ((n-1)/n)*f1*(f1-1)/(2*(f2+1))
        Schao1Var = f1*(f1-1)/2 + f1*((2*f1 - 1)**2)/4 - (f1**4)/(4*Schao1)
    else:    
        Schao1 = Sobs
        Schao1varSum1 = 0.0
        Schao1varSum2 = 0.0
        for v in fValues:            
            Schao1varSum1 += fValues[v]*(math.exp(-1.0*v) -math.exp(-2.0*v))
            Schao1varSum2 += v*math.exp(-1.0*v)*fValues[v]
        Schao1Var = Schao1varSum1 - (Schao1varSum2**2)/n

    return Schao1, Schao1Var


# Compute Chao1 estimator based on abundance data
def chao2Estimate(sampleList):
    
    # find element counts    
    elementCounts = {}
    for sample in sampleList:
        for e in sample:
            if e not in elementCounts:
                elementCounts[e] = 1.0
            else:
                elementCounts[e] += 1.0
    
    # compute Sobs, QValues
    Sobs = len(elementCounts)
    QValues = {}
    for e in elementCounts:
        if elementCounts[e] not in QValues:
            QValues[elementCounts[e]] = 1.0
        else:
            QValues[elementCounts[e]] += 1.0
    
    Schao2 = 0.0 
    Schao2Var = 0.0
    
    if 1.0 in QValues:
        Q1 = QValues[1.0]
    else:
        Q1 = 0.0
    if 2.0 in QValues:
        Q2 = QValues[2.0]
    else:
        Q2 = 0.0
    
    m = float(len(sampleList))
    
    if Q1 > 0.0 and Q2 > 0.0:
        Schao2 = Sobs + ((m-1)/m)*Q1*(Q1-1)/(2*(Q2+1))
        Schao2Var = ((m-1)/m)*Q1*(Q1-1.0)/(2*Q2+1) + (((m-1)/m)**2)*Q1*((2*Q1-1)**2)/(4*((Q2+1)**2)) + (((m-1)/m)**2)*(Q1**2)*Q2*((Q1-1)**2)/(4*((Q2+1)**2))
    elif Q1 > 0.0 and Q2 == 0.0:
        Schao2 = Sobs + ((m-1)/m)*Q1*(Q1-1)/(2*(Q2+1))
        Schao2Var = ((m-1)/m)*Q1*(Q1-1)/2 + (((m-1)/m)**2)*Q1*((2*Q1 - 1)**2)/4 - (((m-1)/m)**2)*(Q1**4)/(4*Schao2)
    else:    
        Schao2 = Sobs
        Schao2varSum1 = 0.0
        Schao2varSum2 = 0.0
        for v in QValues:            
            Schao2varSum1 += QValues[v]*(math.exp(-1.0*v) -math.exp(-2.0*v))
            Schao2varSum2 += v*math.exp(-1.0*v)*QValues[v]
        Schao2Var = Schao2varSum1 - (Schao2varSum2**2)/m
    
    return Schao2, Schao2Var


# Compute Chao estimator based on abundance data
def chao92Estimate(sample):
    
    # find element counts
    
    elementCounts = {}
    for e in sample:
        if e not in elementCounts:
            elementCounts[e] = 1.0
        else:
            elementCounts[e] += 1.0
    
    # compute Sobs, fValues
    Sobs = len(elementCounts)
    fValues = {}
    for e in elementCounts:
        if elementCounts[e] not in fValues:
            fValues[elementCounts[e]] = 1.0
        else:
            fValues[elementCounts[e]] += 1.0
    
    if 1.0 in fValues:
        f1 = fValues[1.0]
    else:
        f1 = 0.0
    if 2.0 in fValues:
        f2 = fValues[2.0]
    else:
        f2 = 0.0
    
    n = float(len(sample))
    
    Chat = 1 - f1/n
    gammaSum = 0.0
    if (Chat == 0):
        return Sobs, 0.0
         
    for v in fValues:            
         gammaSum += v*(v-1)*fValues[v]
         
    gamma = (Sobs/Chat)*gammaSum/(n*(n-1)) - 1
    gamma = max(gamma,0)
    SChao92 = Sobs/Chat + n*(1-Chat)*gamma/Chat
    
    # Compute variance
    SChao92Var = 0.0
    if (gamma > 0):
        sumFi = 0    
        sumiFi = 0
        sumii_oneFi = 0
        
        for i in fValues:
            sumFi += fValues[i]
            sumiFi += i*fValues[i]
            sumii_oneFi += i*(i-1)*fValues[i]
        
        # Compute derivatives
        dFvalues = {}

        a = sumFi - f1
        n = sumiFi - f1
        b = sumii_oneFi - f1

        dFvalues[1.0] = a*(b*(f1**2 + 2*f1*(n-1) + (n-1)*n) + n*(f1+n-1)**2 + b*f1*(2*f1**2 + f1*(4*n -3) + 2*(n-1)*n))/ (n**2 *(f1 + n -1)**2)
        fValues[1.0] = f1
                
        for i in fValues:
            if (i == 1.0):
                continue
            a = sumFi - fValues[i]
            b = sumiFi - i*fValues[i]
            g = sumii_oneFi - i*(i-1)*fValues[i]
            k = i*(i-1)
            f = fValues[i]

            dFvalues[i] = (1/b**2)*((b + f)**2)*((b*f1*(a*(g*(-2*b - 2*f + f1 + 1) - f1*(-1.0*(b**2) + b*f1 + b + f**2 - f1)) + b**2*(2*f*f1 + g)- b*(2*f*f1*(-f + f1 + 1) + g*(f1+1)) - f**2*g - (f**2)*(f1**2) - f**2*f1 + 2*f*f1**2 + g*f1))/((b+f-1)**2*(b+f)*(b+f-f1)**2)+(b*f1*(((a+f)*(f*f1+g))/((b+f-1)*(b+f-f1)) - 1))/(b+f)**2 + b*(a+f)/((b+f)**2) -f/(b+f) + 1)
        
        for i in dFvalues:
            for j in dFvalues:
                if i == j:
                    SChao92Var += dFvalues[i]*dFvalues[j]*fValues[i]*(1-fValues[i]/SChao92)
                else:
                    SChao92Var += dFvalues[i]*dFvalues[j]*(-1.0*fValues[i]*fValues[j]/SChao92)
    
    return SChao92, SChao92Var

def testChao92(entryList,qS,tQ):
    print 'Testing Chao 92 estimator for Restaurants'
    expValue = []
    variance = []
    unique = []
    rateEntries = []

    sample = sampleKList(entryList,qS)
    #sample.extend(sampleK(busHierarchy['root']['Restaurants'],qS))
    Schao92, Schao92Var = chao92Estimate(sample)
    sampleUniqueOld = len(set(sample))
    #print Schao92, Schao92Var, sampleUniqueOld, sampleUniqueOld
    expValue.append(Schao92)
    variance.append(Schao92Var)
    unique.append(sampleUniqueOld)
    rateEntries.append(sampleUniqueOld)
    
    
    for i in range(tQ):
        sample.extend(sampleKList(entryList,qS))        
        Schao92, Schao92Var = chao92Estimate(sample)
        sampleUniqueNew = len(set(sample))
        rate = sampleUniqueNew - sampleUniqueOld
        sampleUniqueOld = sampleUniqueNew
        #print Schao92, Schao92Var, sampleUniqueNew, rate
        expValue.append(Schao92)
        variance.append(Schao92Var)
        unique.append(sampleUniqueNew)
        rateEntries.append(rate)
    plotTitle = 'Chao92_qSize='+str(qS)+'_totQueries='+str(tQ)
    printMultPlots(expValue,unique,rateEntries,plotTitle, tQ)
    plotTitle += '_Var' 
    printVariance(variance,plotTitle, tQ)



def testChao1(entryList,qS,tQ):
    print 'Testing Chao 1 estimator for Restaurants'
    expValue = []
    variance = []
    unique = []
    rateEntries = []

    sample = sampleKList(entryList,qS)
    Schao1, Schao1Var = chao1Estimate(sample)
    sampleUniqueOld = len(set(sample))
    #print Schao1, Schao1Var, sampleUniqueOld, sampleUniqueOld
    expValue.append(Schao1)
    variance.append(Schao1Var)
    unique.append(sampleUniqueOld)
    rateEntries.append(sampleUniqueOld)
    
    for i in range(tQ):
        sample.extend(sampleKList(entryList,qS))
        Schao1, Schao1Var = chao1Estimate(sample)
        sampleUniqueNew = len(set(sample))
        rate = sampleUniqueNew - sampleUniqueOld
        sampleUniqueOld = sampleUniqueNew
        #print Schao1, Schao1Var, sampleUniqueNew, rate
        expValue.append(Schao1)
        variance.append(Schao1Var)
        unique.append(sampleUniqueNew)
        rateEntries.append(rate)
    plotTitle = 'Chao1_qSize='+str(qS)+'_totQueries='+str(tQ)
    printMultPlots(expValue,unique,rateEntries,plotTitle, tQ)
    plotTitle += '_Var' 
    printVariance(variance,plotTitle, tQ)

def testChao2(entryList, qS, tQ):
    print '\n\nTesting Chao 2 estimator for Restaurants'
    expValue = []
    variance = []
    unique = []
    rateEntries = []
    
    sampleList = [] 
    sample = []
    sampleList.append(sampleKList(entryList,qS))
    sample.extend(sampleList[0])
    Schao2, Schao2Var = chao2Estimate(sampleList)
    sampleUniqueOld = len(set(sample))
    #print Schao2, Schao2Var,sampleUniqueOld, sampleUniqueOld
    expValue.append(Schao2)
    variance.append(Schao2Var)
    unique.append(sampleUniqueOld)
    rateEntries.append(sampleUniqueOld)
    
    for i in range(tQ):
        sampleList.append(sampleKList(entryList,qS))
        sample.extend(sampleList[i+1])
        Schao2, Schao2Var = chao2Estimate(sampleList)
        sampleUniqueNew = len(set(sample))
        rate = sampleUniqueNew - sampleUniqueOld
        sampleUniqueOld = sampleUniqueNew
        #print Schao2, Schao2Var, sampleUniqueNew, rate
        expValue.append(Schao2)
        variance.append(Schao2Var)
        unique.append(sampleUniqueNew)
        rateEntries.append(rate)
    plotTitle = 'Chao2_qSize='+str(qS)+'_totQueries='+str(tQ)
    printMultPlots(expValue,unique,rateEntries,plotTitle, tQ)
    plotTitle += '_Var' 
    printVariance(variance,plotTitle, tQ)

def printMultPlots(expValue, unique, rate, title,tQ):
    
    font = {'family' : 'serif',
        'color'  : 'darkred',
        'weight' : 'normal',
        'size'   : 16,
    }
    
    x = np.linspace(0.0, 2.0, tQ+1)
    yExp = np.array(expValue)
    yUnique = np.array(unique)
    yRate = np.array(rate)

    plt.plot(x, yExp, 'k--', x, yUnique, 'k:', x, yRate, 'k')
    plt.legend(('Expected', 'Unique', 'Rate/new'),
           'upper left', shadow=True)
    plt.title(title, fontdict=font)
    plt.xlabel('# queries', fontdict=font)
    plt.ylabel('# items', fontdict=font)
    plt.legend()

    # Tweak spacing to prevent clipping of ylabel
    plt.subplots_adjust(left=0.15)
    fileName = '/Users/thodoris/Documents/ThodPh.D./Papers/YelpSimulation/figs/reviews/' + title + '.pdf'
    plt.savefig(fileName)
    plt.close()

def printVariance(variance, title,tQ):
    
    font = {'family' : 'serif',
        'color'  : 'darkred',
        'weight' : 'normal',
        'size'   : 16,
    }
    
    x = np.linspace(0.0, 2.0, tQ+1)
    yVar = np.array(variance)
    
    plt.plot(x, yVar,'k')
    plt.title(title, fontdict=font)
    plt.xlabel('# queries', fontdict=font)
    plt.ylabel('Variance', fontdict=font)
    plt.legend()
    
    # Tweak spacing to prevent clipping of ylabel
    plt.subplots_adjust(left=0.15)
    fileName = '/Users/thodoris/Documents/ThodPh.D./Papers/YelpSimulation/figs/reviews/' + title + '.pdf'
    plt.savefig(fileName)
    plt.close()
            

def main(argv):
    
    # Set input data filename
    filename = argv[1]

    # Read input data
    yelp_data_file = open(filename,'r')
    yelp_Data = []
    for l in yelp_data_file:
     yelp_Data.append(json.loads(l))

    # Initialize hierarchies
    location = {}
    business = {}
    business['N/A'] = {}

    for e in yelp_Data:
        state = e['state']
        city  = e['city']
        business_id = e['business_id']
        review_count = e['review_count']
        stars = e['stars']
        business_cat = e['categories']

        if state not in location:
            location[state] = {}
            location[state][city] = {}
            location[state][city][business_id]= [business_id,float(stars),float(review_count)]
        else:
            if city not in location[state]:
                location[state][city] = {}
                location[state][city][business_id]= [business_id,float(stars),float(review_count)]
            else:
                location[state][city][business_id]= [business_id,float(stars),float(review_count)]

        if len(business_cat) == 0:
            business['N/A'][business_id]= [business_id,float(stars),float(review_count)]
        for cat in business_cat:
            if (cat not in business):
                business[cat] = {}
                business[cat][business_id]= [business_id,float(stars),float(review_count)]
            else:
                business[cat][business_id]= [business_id,float(stars),float(review_count)]
            
    # Determine internal vs leaf nodes 
    internalNode = {}
    for cat1 in business:
        for cat2 in business:
            if cat1 != cat2:
                cat1Entries = set(business[cat1].keys())
                cat2Entries = set(business[cat2].keys())
                if cat2Entries.issubset(cat1Entries):
                    if cat1 not in internalNode:
                        internalNode[cat1] = []
                        internalNode[cat1].append(cat2)
                    else:
                        internalNode[cat1].append(cat2)

    # Build business hierarchy
    busHierarchy = {}
    busHierarchy['root'] = {}
    for cat in internalNode:
        if len(internalNode[cat]) > 1:
            busHierarchy['root'][cat] = {}
            for inCat in internalNode[cat]:
                busHierarchy['root'][cat][inCat] = {}
                for bId in business[inCat]:
                        busHierarchy['root'][cat][inCat][bId] = business[inCat][bId]                

    visited = []
    uniqueRestaurants = []
    uniques = 0
    for e in list(flatten_dict(busHierarchy['root']['Restaurants'])):
        if e[0] not in visited:
            uniques += 1
            uniqueRestaurants.append(e)
        visited.append(e[0])

    print 'Total number of restaursnts = ',uniques

    # generate plots
            
    qS = [10,50,200]
    tQ = [5,200,400]
    
    for q in qS:
        for t in tQ:
            testChao1(uniqueRestaurants,q,t)
            testChao2(uniqueRestaurants,q,t)
            testChao92(uniqueRestaurants,q,t)
    
if __name__ == "__main__":
    main(sys.argv)


