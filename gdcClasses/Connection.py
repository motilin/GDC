from pymongo import MongoClient

class Connection:

    def __init__(self):
        self.client = MongoClient('localhost')
        self.db = self.client.gdc

    def get(self):
        return self.db
