from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, request
from werkzeug.exceptions import HTTPException

import config
from web_api.response_builders import build_response, get_404, get_400, update_or_init, join_dicts

app = Flask(__name__)


@app.route(config.api_url_start, methods=['GET'])
@app.route('%s/<item_id>' % config.api_url_start, methods=['GET'])
def get_tasks(item_id=None):
    client = MongoClient()
    db = client.tasks_db
    query_filter = {}

    if item_id is not None:
        try:
            query_filter['_id'] = ObjectId(item_id)
        except InvalidId as _:
            return get_400()
        cursor = db.tasks.find(query_filter)
        if cursor.count() == 0:
            return get_404()
    else:
        cursor = db.tasks.find()

    return build_response(
        items_cursor=cursor
    )


@app.route(config.api_url_start, methods=['POST'])
@app.route('%s/<item_id>' % config.api_url_start, methods=['POST'])
def add_edit_item(item_id=None):
    client = MongoClient()
    db = client.tasks_db
    query_filter = {}

    try:
        new_data = request.json
    except HTTPException as e:
        if e.code == 400:
            return get_400()
        else:
            return build_response(
                status=e.description,
                status_code=e.code
            )

    if item_id is not None:
        try:
            query_filter['_id'] = ObjectId(item_id)
            old_item = db.tasks.find_one(query_filter)
            db.tasks.replace_one(query_filter, join_dicts(old_item, new_data))
            return build_response(items_cursor=db.tasks.find(query_filter))
        except InvalidId as _:
            return get_404()
    else:
        res = db.tasks.insert_one(update_or_init(new_data))
        query_filter['_id'] = res.inserted_id
        return build_response(items_cursor=db.tasks.find(query_filter))
