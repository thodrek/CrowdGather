__author__ = 'thodrek'


class PointEstimate:

    def __init__(self,latticePoint):
        self.point = latticePoint

        # exclude list variables
        self.excludeList = []