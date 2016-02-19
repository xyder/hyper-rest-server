from flask import Flask, request
from werkzeug.exceptions import HTTPException

import config
from web_api.api_lib import Item, HttpStatus
from web_api.db_functions import get_id_filter, get_db
from web_api.response_builders import build_response

app = Flask(__name__)
app.config['api.vars'] = config


@app.route(app.config['api.vars'].api_url_start, methods=['GET'])
def get_start():
    """
    View that retrieves an empty list of items with all available actions on list.
    :return:
    """
    return build_response()


@app.route('%s/list' % app.config['api.vars'].api_url_start, methods=['GET'])
@app.route('%s/<item_id>' % app.config['api.vars'].api_url_start, methods=['GET'])
def get_tasks(item_id=None):
    """
    View that retrieves an item or the list of items.
    :param item_id: the id of the item
    :return: the HTTP response containing the list of all items or a single item if an id was specified.
    """

    db = get_db(app)

    # if no id given, send list of all items
    if not item_id:
        return build_response(items_cursor=db.tasks.find())

    # build the id filter and return 400 if not valid
    query_filter = get_id_filter(item_id)
    if not query_filter:
        return build_response(**HttpStatus.BAD_REQUEST)

    # search for the item or send 404 if not found
    cursor = db.tasks.find(query_filter)
    if cursor.count() == 0:
        return build_response(**HttpStatus.NOT_FOUND)

    # build and send the result
    return build_response(items_cursor=cursor)


@app.route(app.config['api.vars'].api_url_start, methods=['POST'])
@app.route('%s/<item_id>' % app.config['api.vars'].api_url_start, methods=['POST'])
def add_edit_item(item_id=None):
    """
    View that processes the Add/Edit endpoint.
    :param item_id: the id of the item
    :return: the HTTP response containing the added/altered item.
    """

    # convert and fetch the json from the request
    try:
        new_data = request.json
        if not new_data:
            new_data = {}
    except HTTPException as e:
        # fail with 400 if not a json
        if e.code == 400:
            return build_response(**HttpStatus.BAD_REQUEST)
        else:
            # unknown error, dump it as response
            return build_response(
                    status=e.description,
                    status_code=e.code
            )

    db = get_db(app)

    # no id specified, it means it will add a new item
    if not item_id:
        res = db.tasks.insert_one(Item(**new_data).get_clean_attributes())
        query_filter = get_id_filter(res.inserted_id)
        # returns the newly created item
        return build_response(items_cursor=db.tasks.find(query_filter))

    # build the id filter and return 400 if not valid
    query_filter = get_id_filter(item_id)
    if not query_filter:
        return build_response(**HttpStatus.NOT_FOUND)

    # update the item by replacing with an updated db document
    item = db.tasks.find_one(query_filter)
    item = Item(**item)
    for k, v in new_data.items():
        setattr(item, k, v)
    db.tasks.replace_one(query_filter, item.get_clean_attributes())
    # send the altered item as response
    return build_response(items_cursor=db.tasks.find(query_filter))


@app.route('%s/<item_id>' % app.config['api.vars'].api_url_start, methods=['DELETE'])
def delete_item(item_id):
    """
    View that processes the Delete endpoint.

    :param item_id: the id of the item
    :return: an empty HTTP response with status code 200 if successful.
    """

    # fail if no id specified
    if not item_id:
        return build_response(**HttpStatus.BAD_REQUEST)

    # build the id filter and return 400 if not valid
    query_filter = get_id_filter(item_id)
    if not query_filter:
        return build_response(**HttpStatus.NOT_FOUND)

    db = get_db(app)

    # attempt to delete the item from the database
    result = db.tasks.delete_one(query_filter)
    if result.deleted_count == 0:
        # no records deleted means no items with that id found.
        return build_response(**HttpStatus.NOT_FOUND)

    # return an empty response with status code 200 and the record_count equal to deleted records count
    return build_response(count=result.deleted_count)
