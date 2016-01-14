from flask import Flask, request
from werkzeug.exceptions import HTTPException

import config
from web_api.db_functions import get_id_filter, get_db
from web_api.response_builders import build_response, get_404, get_400, update_or_init, join_dicts

app = Flask(__name__)
app.config['api.vars'] = config


@app.route(app.config['api.vars'].api_url_start, methods=['GET'])
@app.route('%s/<item_id>' % app.config['api.vars'].api_url_start, methods=['GET'])
def get_tasks(item_id=None):
    db = get_db(app)

    if not item_id:
        return build_response(items_cursor=db.tasks.find())

    query_filter = get_id_filter(item_id)
    if not query_filter:
        return get_400()

    cursor = db.tasks.find(query_filter)
    if cursor.count() == 0:
        return get_404()

    return build_response(items_cursor=cursor)


@app.route(app.config['api.vars'].api_url_start, methods=['POST'])
@app.route('%s/<item_id>' % app.config['api.vars'].api_url_start, methods=['POST'])
def add_edit_item(item_id=None):
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

    db = get_db(app)

    if not item_id:
        res = db.tasks.insert_one(update_or_init(new_data))
        query_filter = get_id_filter(res.inserted_id)
        return build_response(items_cursor=db.tasks.find(query_filter))

    query_filter = get_id_filter(item_id)
    if not query_filter:
        return get_404()

    old_item = db.tasks.find_one(query_filter)
    db.tasks.replace_one(query_filter, join_dicts(old_item, new_data))
    return build_response(items_cursor=db.tasks.find(query_filter))


@app.route('%s/<item_id>' % app.config['api.vars'].api_url_start, methods=['DELETE'])
def delete_item(item_id):
    if not item_id:
        return get_400()

    query_filter = get_id_filter(item_id)

    if not query_filter:
        return get_404()

    db = get_db(app)

    result = db.tasks.delete_one(query_filter)
    if result.deleted_count == 0:
        return get_404()

    return build_response(count=result.deleted_count)

