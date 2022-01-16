from pymongo import MongoClient


class MongoDal(object):
    def __init__(self, db_name, collection_name):
        mongoclient = MongoClient('localhost', 27017)
        # mongoclient = MongoClient('mongodb://localhost:27017')

        database = mongoclient[db_name]
        self._collection = database[collection_name]

    # Create operations
    def insert(self, document):
        return self._collection.insert_one(document)

    def insert_many(self, documents):
        return self._collection.insert_many(documents)

    # Read operations
    def read_all(self):
        return self._collection.find()

    def read_many(self, conditions):
        return self._collection.find(conditions)

    def read(self, conditions):
        return self._collection.find_one(conditions)

    # Update operations
    def update(self, conditions, new_value):
        return self._collection.update_one(conditions, new_value)

    # Delete operations
    def delete(self, condition):
        return self._collection.delete_one(condition)

    def delete_many(self, condition):
        return self._collection.delete_many(condition)

'''
    def increment_age(self, conditions):
        return self._users.update_one(conditions, {'$inc': {'age': 1}})
'''