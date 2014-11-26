__author__ = 'thodrek'
# Define Lattice Class
import genutils
import LatticePoint
import sys
import DBManager

class Lattice:
    def __init__(self, hDicts, hDesc, itemInfo):
        # store description of hierarchies
        self.hDesc = hDesc

        # store pointer to item info
        self.itemInfo = itemInfo

        # initialize DB manager
        self.db = DBManager.DBManager()

        keysInDB = self.db.getSize()
        if keysInDB == 0:
            print "Store Populations...ENABLED."
            persist = True
        else:
            print "Populations already present. "+str(keysInDB)+" keys found."
            persist = False
        self.points = self.constructPoints(hDicts,persist)
        if persist:
            self.db.saveToDisk()


    def constructPoints(self,hDicts,persist):
        # initialize points
        points = {}

        # get all items key - item combinations for single hierarchy
        print 'Constructing flat list of lattice points...',
        hLists = [genutils.lattice_points_list(h) for h in hDicts]
        lattice_point_list = genutils.cross(*hLists)
        print 'DONE'

        # construct lattice points
        print 'Constructing lattice nodes...'
        counter = 0
        for point in lattice_point_list:
            # initialize key and items
            point_key = point[0][0]
            point_items = []

            # generate key and items
            if persist:
                point_items = set(point[0][1])

            for idx in range(1,len(hDicts)):
                point_key += '|'+point[idx][0]
                if persist:
                    point_items &= set(point[idx][1])

            # generate lattice point
            newPoint = LatticePoint.LatticePoint(point_key,self.db,self.hDesc,self)

            if persist:
                self.db.addKeySET(point_key,point_items)

            # assign to point dictionaries
            points[point_key] = newPoint

            # print progress
            counter += 1
            progress = float(counter)*100.0/float(len(lattice_point_list))
            sys.stdout.write("\r%.2f%% (%d out of %d)" % (progress, counter, len(lattice_point_list)))
            sys.stdout.flush()
        print 'DONE'

        # iterate over lattice points and assign parents and descendants
        # There are three cases: (i) no values are assigned, i.e., root, (ii) only one value assigned, (ii) more than one values assigned
        print 'Creating lattice edges...'
        counter = 0
        for pointKey in points:
            p = points[pointKey]
            # check if the point is a root
            if p.getTotalAssignedValues() == 0:
                continue
            # if only one value is assigned only one parent exists
            elif p.getTotalAssignedValues() == 1:
                # extract parent key
                parentKey = ''
                tokens = pointKey.split('|')
                if '_' in tokens[0]:
                    parentKey = '_'.join(tokens[0].split('_')[:-1])
                for i in range(1,len(tokens)):
                    parentKey += '|'
                    if '_' in tokens[i]:
                        parentKey += '_'.join(tokens[i].split('_')[:-1])

                # grab parent
                parentPoint = points[parentKey]

                # assign parent
                p.assignParent(parentPoint)

                # assign descendant
                parentPoint.assignDescendant(p)
            # multiple values are assigned. Point has multiple parents
            # corresponding to all leave-one out value assignments
            else:
                # extract parent keys
                tokens = pointKey.split('|')
                for i in range(len(tokens)):
                    if tokens[i] == '':
                        continue
                    setValue = tokens[i]
                    tokens[i] = ''
                    parentKey = '|'.join(tokens)

                    # grab parent
                    parentPoint = points[parentKey]

                    # assign parent
                    p.assignParent(parentPoint)

                    # assign descendant
                    parentPoint.assignDescendant(p)

                    # reset tokens
                    tokens[i] = setValue

            # print progress
            counter += 1
            progress = float(counter)*100.0/float(len(points))
            sys.stdout.write("\r%.2f%% (%d out of %d)" % (progress, counter, len(points)))
            sys.stdout.flush()
        print 'DONE'

        return points

    def getLatticeSize(self):
        return len(self.points)

    def clearLatticeSamples(self):
        for p in self.points:
            self.points[p].clearSampledPopulation()

    def getItemWeights(self,itemSet):
        itemList = []
        for item in itemSet:
            weight = self.itemInfo[item]['weight']
            if not weight or weight=='':
                weight = 1.0
            itemList.append((item, weight))
        return itemList

