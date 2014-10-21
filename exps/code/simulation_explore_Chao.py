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
    sample = []
    nodeInfo = {}
    nodeInfo['root'] = {}
    nodeInfo['root']['unique'] = []
    nodeInfo['root']['quadrats'] = 0.0
    nodeInfo['root']['sampleSize'] = []
    nodeInfo['root']['missData'] = []
    nodeInfo['root']['totalData'] = samplingutils.totalPopulation(hierarchyNode)

    for c in hierarchyNode:
        nodeInfo[c] = {}
        nodeInfo[c]['sample'] = []
        nodeInfo[c]['unique'] = []
        nodeInfo[c]['quadrats'] = 0.0
        nodeInfo[c]['sampleSize'] = []
        nodeInfo[c]['missData'] = []
        nodeInfo[c]['totalData'] = samplingutils.totalPopulation(hierarchyNode[c])

    # get initial sample
    newSample = samplingutils.sampleKList(hierarchyNodeCont,querySize)
    sample.extend(newSample)
    nodeInfo['root']['unique'].append(len(set(sample)))
    nodeInfo['root']['quadrats'] += 1.0
    nodeInfo['root']['sampleSize'].append(len(sample))
    nodeInfo['root']['missData'].append(-1.0)

    childSample = assignSampleToChildren(hierarchyNode,sample)
    for c in hierarchyNode:
        if c in childSample:
            nodeInfo[c]['sample'].extend(childSample[c])
            nodeInfo[c]['unique'].append(len(set(nodeInfo[c]['sample'])))
            nodeInfo[c]['quadrats'] += 1.0
            nodeInfo[c]['sampleSize'].append(len(nodeInfo[c]['sample']))
            nodeInfo[c]['missData'].append(-1.0)
        else:
            nodeInfo[c]['unique'].append(0.0)
            nodeInfo[c]['sampleSize'].append(0.0)
            nodeInfo[c]['missData'].append(-1.0)


    # Get sample
    for i in range(1,totalBudget):
        # Get new sample
        newSample = samplingutils.sampleKList(hierarchyNodeCont,querySize)
        sample.extend(newSample)

        # Update root info
        nodeInfo['root']['unique'].append(len(set(sample)))
        nodeInfo['root']['quadrats'] += 1.0
        nodeInfo['root']['sampleSize'].append(len(sample))
        rSingles = numberOfSingletons(sample)
        rPairs = numberOfPairs(sample)

        t = nodeInfo['root']['quadrats'] + 1.0
        q = t/1000.0
        newMissData = float(rSingles*rSingles)/float(2*t*rPairs/(t-1.0) + q*rSingles/(1-q))
        nodeInfo['root']['missData'].append(newMissData)

        # Update children info
        childSample = assignSampleToChildren(hierarchyNode,sample)
        for c in hierarchyNode:
            if c in childSample:
                nodeInfo[c]['sample'].extend(childSample[c])
            nodeInfo[c]['unique'].append(len(set(nodeInfo[c]['sample'])))
            nodeInfo[c]['quadrats'] += 1.0
            nodeInfo[c]['sampleSize'].append(len(nodeInfo[c]['sample']))
            if nodeInfo[c]['quadrats'] > 1.0:
                rSingles = numberOfSingletons(nodeInfo[c]['sample'])
                rPairs = numberOfPairs(nodeInfo[c]['sample'])

                t = nodeInfo[c]['quadrats'] + 1.0
                q = t/1000.0
                try:
                    newMissData = float(rSingles*rSingles)/float(2*t*rPairs/(t-1.0) + q*rSingles/(1-q))
                    nodeInfo[c]['missData'].append(newMissData)
                except:
                    nodeInfo[c]['missData'].append(-8.0)
            else:
                nodeInfo[c]['missData'].append(-1.0)


    return nodeInfo


def assignSampleToChildren(root,sample):
    childSample = {}
    for e in sample:
        activeChildren = samplingutils.findChildrenNodes(root,e)
        for c in activeChildren:
            if c not in childSample:
                childSample[c] = []
            childSample[c].append(e)
    return childSample


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

    # Start sampling for node
    #querySizes = [1,2,3,4,5,6,10,15,20,25,30,35,40,45,50,60,100]
    querySizes = [5]
    for qS in querySizes:
        nodeInfo = sampleData(busHierarchy['root']['Restaurants'],uniqueEntries,qS,50)
        cols = len(nodeInfo['root']['unique'])
        for i in range(cols):
            print str(qS)+"\t",
            for n in nodeInfo:
                print n+"\t"+str(nodeInfo[n]['unique'][i])+"\t"+str(nodeInfo[n]['quadrats'])+"\t"+str(nodeInfo[n]['sampleSize'][i])+"\t"+str(nodeInfo[n]['missData'][i])+"\t"+str(nodeInfo[n]['totalData'])+"\t",
            print ''


if __name__ == "__main__":
    main(sys.argv)