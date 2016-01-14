from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient


def get_id_filter(item_id):
    try:
        return {
            '_id': ObjectId(item_id)
        }
    except InvalidId as _:
        return None


def get_db(app):
    client = MongoClient()
    return client[app.config['api.vars'].db_name]
