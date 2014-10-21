import sys
import samplingutils
import json
import estimators


def initHierarchy(dataFile):
    # Initialize hierarchies
    location = {}
    business = {}
    business['N/A'] = {}

    for e in dataFile:
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

    return business

def createHierarchy(dict):
    # Determine internal vs leaf nodes
    internalNode = {}
    for cat1 in dict:
        for cat2 in dict:
            if cat1 != cat2:
                cat1Entries = set(dict[cat1].keys())
                cat2Entries = set(dict[cat2].keys())
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
                for bId in dict[inCat]:
                        busHierarchy['root'][cat][inCat][bId] = dict[inCat][bId]

    return busHierarchy


def computeUniqueItems(hierarchyNode):
    visited = []
    uniqueEntries = []
    uniques = 0
    for e in list(samplingutils.flatten_dict(hierarchyNode)):
        if e[0] not in visited:
            uniques += 1
            uniqueEntries.append(e)
        visited.append(e[0])
    return uniques, uniqueEntries

def updateChildrenSamples(newSample, childrenMap, childrenSamples, childrenChars,count=False):
    for entry in newSample:
        for i in childrenMap:
            childNode = childrenMap[i]
            if samplingutils.belongsTo(childNode, entry) == 1:
                # update child sample
                childrenSamples[i].append(entry)
                # update child total uniques
                newTotal = len(childrenSamples[i])
                newUnique = len(set(childrenSamples[i]))
                print newTotal, newUnique
                childrenChars[i]['total'].append(newTotal)
                childrenChars[i]['unique'].append(newUnique)
                if count:
                    childrenChars[i]['initSize'] += 1

def updateChildrenEstimates(childrenChars,childrenEstimates):
    for childId in childrenChars:
        if len(childrenChars[childId]['total']) > 5:
            try:
                childObservedData = [childrenChars[childId]['total'],  childrenChars[childId]['unique']]
                sampleSize, uEntities = estimators.trainPredictVARMA(childObservedData)
                childrenEstimates[childId]['total'].append(sampleSize)
                childrenEstimates[childId]['unique'].append(uEntities)
            except:
                print childObservedData


def sampleEstimate(hierarchyNode, hierarchyNodeCont,querySize,initBudget,totalBudget):
    uniqueEntities = []
    totalEntities = []

    uE_Predicted = []
    tE_Predicted = []
    uE_Actual = []
    tE_Actual = []

    # Initialize children nodes
    childrenMap = {}
    childrenSamples = {}
    childrenChars = {}
    childrenEstimates = {}

    i = 0
    for c in hierarchyNode:
        childrenMap[i] = hierarchyNode[c]

        childrenSamples[i] = {}
        childrenSamples[i] = []

        childrenChars[i] = {}
        childrenChars[i]['total'] = []
        childrenChars[i]['unique'] = []
        childrenChars[i]['initSize'] = 0

        childrenEstimates[i] = {}
        childrenEstimates[i]['total'] = []
        childrenEstimates[i]['unique'] = []

        i+=1


    # Take initial samples
    sample = []
    for i in range(initBudget):
        newSample = samplingutils.sampleKList(hierarchyNodeCont,querySize)
        sample.extend(newSample)
        uniqueEntities.append(len(set(sample)))
        totalEntities.append(len(sample))
        updateChildrenSamples(newSample, childrenMap, childrenSamples, childrenChars,True)


    # Estimate next step with Vector ARMA. Then sample to verify
    for i in range(totalBudget):
        # Form observed data
        observedData = [totalEntities,uniqueEntities]
        # Get predicted values
        sampleSize, uEntities = estimators.trainPredictVARMA(observedData)
        uE_Predicted.append(uEntities)
        tE_Predicted.append(sampleSize)

        # Get real values
        newSample = samplingutils.sampleKList(hierarchyNodeCont,querySize)
        sample.extend(newSample)
        uE_Actual.append(len(set(sample)))
        tE_Actual.append(len(sample))
        uniqueEntities.append(len(set(sample)))
        totalEntities.append(len(sample))

        # Update estimates for children
        updateChildrenEstimates(childrenChars,childrenEstimates)
        updateChildrenSamples(newSample, childrenMap, childrenSamples, childrenChars)

    return uE_Predicted,tE_Predicted,uE_Actual,tE_Actual, childrenChars, childrenEstimates








def main(argv):
    # Prelims
    # Set input data filename
    filename = argv[1]

    # Read input data
    yelp_data_file = open(filename,'r')
    yelp_Data = []
    for l in yelp_data_file:
     yelp_Data.append(json.loads(l))


    # Initialize hierarchies
    business = initHierarchy(yelp_Data)

    # Create hierarchies
    busHierarchy = createHierarchy(business)

    # Start exps
    # Find unique entries
    uniques, uniqueEntries = computeUniqueItems(busHierarchy['root']['Restaurants'])
    print 'Total number of restaurants = ',uniques

    # Start sampling and test Vector ARMA for node and children
    uE_Predicted,tE_Predicted,uE_Actual,tE_Actual, childrenChars, childrenEstimates = sampleEstimate(busHierarchy['root']['Restaurants'],uniqueEntries,5,5,100)


    print "\n Estimations for node"
    print uE_Predicted,uE_Actual
    print "\n"
    print tE_Predicted, tE_Actual
    print "\n"

    print "\n Estimations for children"
    i = 0
    for c in childrenChars:
        print len(childrenChars[c]['total'])
        if len(childrenChars[c]['total']) > 5:
            print "\n New Child"
            print childrenChars[c]['total']
            print childrenChars[c]['unique']
            print childrenEstimates[c]['total']
            print childrenEstimates[c]['unique']
            i += 1

if __name__ == "__main__":
    main(sys.argv)