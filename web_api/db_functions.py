from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient


def get_id_filter(item_id):
    """
    Function that returns a dict with an ObjectId stored as value for the key '_id'
    :param item_id: the id used when creating the ObjectId
    :return: the resulting dict.
    """

    try:
        return {
            '_id': ObjectId(item_id)
        }
    except InvalidId as _:
        return None


def get_db(app):
    """
    Function that creates a client for Mongo and retrieves the database based on the config vars.
    :param app: the Flask app.
    :return: the db object.
    """

    client = MongoClient()
    return client[app.config['api.vars'].db_name]
