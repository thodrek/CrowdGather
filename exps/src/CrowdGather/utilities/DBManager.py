__author__ = 'thodrek'
import redis

class DBManager:
        def __init__(self):
            self.server = redis.Redis("localhost")

        def addKeySET(self,key,value):
            valueString = repr(value)
            self.server.set(key,valueString)

        def getKeySET(self,key):
            valueString = self.server.get(key)
            return eval(valueString)

        def saveToDisk(self):
            return self.server.bgsave()

        def getSize(self):
            return self.server.dbsize()