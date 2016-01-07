from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask

import config
from web_api.response_builders import build_response

app = Flask(__name__)


@app.route('/api/v%s/tasks' % config.api_version, methods=['GET'])
def get_tasks():
    client = MongoClient()
    db = client.tasks_db
    return build_response(
        items_cursor=db.tasks.find()
    )


@app.route('/api/v%s/tasks/<item_id>' % config.api_version, methods=['GET'])
def get_task(item_id):
    client = MongoClient()
    db = client.tasks_db
    try:
        item_id = ObjectId(item_id)
    except InvalidId as _:
        return build_response(
            status='Not Found.',
            status_code=404
        )
    return build_response(
        items_cursor=db.tasks.find({'_id': item_id})
    )
