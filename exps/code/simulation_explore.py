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
    return uniques, uniqueEntries, visited


def sampleData(hierarchyNode,hierarchyNodeCont,querySize,totalBudget):
    uniqueEntities = []
    totalEntities = []
    returnEntities = []
    oldUnique = 0
    sample = []
    singletons = []
    missMass = []
    actMissMass = []
    childrenMissMass = {}
    childrenUnique = {}
    childrenTotal = {}
    missData = []

    newSample = samplingutils.sampleKList(hierarchyNodeCont,querySize)
    sample.extend(newSample)

    # Get sample
    for i in range(1,totalBudget):
        # Get new sample
        newSample = samplingutils.sampleKList(hierarchyNodeCont,querySize)
        sample.extend(newSample)
        newUnique = len(set(sample))
        uniqueEntities.append(len(set(sample)))
        totalEntities.append(len(sample))
        returnValue = newUnique - oldUnique
        oldUnique = newUnique
        returnEntities.append(returnValue)
        newSingletons = numberOfSingletons(sample)
        newPairs = float(numberOfPairs(sample))
        singletons.append(newSingletons)
        newMissMass = float(newSingletons)/float(len(sample))
        missMass.append(newMissMass)
        newActMissMass = actualMissMass(sample,hierarchyNodeCont)
        actMissMass.append(newActMissMass)
        t = float(i + 1)
        q = t/float(1000)
        newMissData = float(newSingletons*newSingletons)/float(2*t*newPairs/(t-1.0) + q*newSingletons/(1-q))
        missData.append(newMissData)

        newEstChildrenMissMass, newActChildrenMissMass, newChildrenUnique, newChildrenTotal = missMassChildren(hierarchyNode,sample)
        for c in newEstChildrenMissMass:
            if c not in childrenMissMass:
                childrenMissMass[c] = {}
                childrenMissMass[c]['act'] = []
                childrenMissMass[c]['est'] = []
                childrenUnique[c] = []
                childrenTotal[c] = []
            childrenMissMass[c]['act'].append(newActChildrenMissMass[c])
            childrenMissMass[c]['est'].append(newEstChildrenMissMass[c])
            childrenUnique[c].append(newChildrenUnique[c])
            childrenTotal[c].append(newChildrenTotal[c])

    return uniqueEntities,returnEntities, singletons, missMass, actMissMass, childrenMissMass, childrenUnique, childrenTotal, missData

def missMassChildren(hierarchyNode,sample):
    childEntries = {}
    childEstMissMass = {}
    childActMissMass = {}
    childUnique = {}
    childTotalSize = {}
    for e in sample:
        for c in hierarchyNode:
            if c not in childEntries:
                childEntries[c] = []
                childEstMissMass[c] = 1.0
                childUnique[c] = 0.0
                totalData = samplingutils.totalPopulation(hierarchyNode[c])
                childTotalSize[c] = totalData
                if totalData > 0:
                    childActMissMass[c] = 1.0
                else:
                    childActMissMass[c] = 0.0
            if samplingutils.belongsTo(hierarchyNode[c],e) == 1:
                childEntries[c].append(e)
    for c in childEntries:
        if len(childEntries[c]) > 0:
            estMissMass = float(numberOfSingletons(childEntries[c]))/float(len(childEntries[c]))
            childEstMissMass[c] = estMissMass

            actMissMass = actualMissMass(childEntries[c],samplingutils.getTotalEntries(hierarchyNode[c]))
            childActMissMass[c] = actMissMass

            childUnique[c] = len(set(childEntries[c]))
    return childEstMissMass, childActMissMass, childUnique, childTotalSize



def numberOfSingletons(sample):
    elementCount = {}
    for i in sample:
        if i not in elementCount:
            elementCount[i] = 0
        elementCount[i] += 1
    singletons = 0
    for i in elementCount:
        if elementCount[i] == 1:
            singletons += 1
    return singletons

def numberOfPairs(sample):
    elementCount = {}
    for i in sample:
        if i not in elementCount:
            elementCount[i] = 0
        elementCount[i] += 1
    pairs = 0
    for i in elementCount:
        if elementCount[i] == 2:
            pairs += 2
    return pairs

def actualMissMass(sample, uniqueEntries):
    covMass = 0.0
    missMass = 0.0
    totalMass = 0.0

    for e in uniqueEntries:
        entryMass = float(e[2])
        if e[0] in sample:
            covMass += entryMass
        else:
            missMass += entryMass
        totalMass += entryMass

    return missMass/totalMass





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
    uniques, uniqueEntries, uniqueEntryIds = computeUniqueItems(busHierarchy['root']['Restaurants'])
    print 'Total number of restaurants = ',uniques
    print 'QuerySize\tUniqueEntries\tReturn\tSingletons\tEstimatedMissMass\tActMissMass\tMissData'

    # Start sampling for node
    #querySizes = [1,2,3,4,5,6,10,15,20,25,30,35,40,45,50,60,100]
    querySizes = [5]
    for qS in querySizes:
        uniqueEntities,returnEntities, singletons, missMass, actMissMass, childrenMissMass, childrenUnique, childrenTotal, missData = sampleData(busHierarchy['root']['Restaurants'],uniqueEntries,qS,50)

        for i in range(len(uniqueEntities)):
            print str(qS)+"\t"+str(uniqueEntities[i])+"\t"+str(returnEntities[i])+"\t"+str(singletons[i])+"\t"+str(missMass[i])+"\t"+str(actMissMass[i])+"\t"+str(missData[i])+"\t",
            for c in childrenMissMass:
                print str(childrenMissMass[c]['est'][i])+"\t"+str(childrenMissMass[c]['act'][i])+"\t"+str(childrenUnique[c][i])+"\t"+str(childrenTotal[c][i])+"\t",
            print ''


if __name__ == "__main__":
    main(sys.argv)