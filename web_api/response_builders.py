from flask import jsonify
import config


class Methods:
    """
    Const struct to store HTTP methods keywords
    """
    POST = 'POST'
    GET = 'GET'
    DELETE = 'DELETE'


def build_link(**kwargs):
    """
    Function that builds a link structure.
    :param kwargs: rel, href, method, args
    :return: a generic link
    """

    ret = {
        'rel': kwargs.get('rel', ''),
        'href': kwargs.get('href', ''),
        'method': kwargs.get('method', Methods.GET),
    }

    if 'args' in kwargs:
        ret['args'] = kwargs['args']

    return ret


def update_or_init(values):
    """
    Function that converts the given values to a task dict and initializes any missing parameters.
    :param values: the values used to store in the task dict
    :return: the task dict
    """

    return {
        'title': values.get('title', ''),
        'body': values.get('body', ''),
        'created': values.get('created') or 0,
        'due': values.get('due') or 0,
        'state': values.get('state', 'open')
    }


def join_kv(dict1, dict2, key, default=None):
    """
    Function that returns the value for the given key search in dict1, then dict2 and sending
    default if it was not found.
    :param dict1: first dict in which it will search.
    :param dict2: 2nd dict in which it will search.
    :param key: the key for which the value will be retrieved
    :param default: a value to be sent if the key was not found in either dict
    :return: the value for the given key or a default value if the key was not found
    """

    return dict1.get(key) if key in dict1 else dict2.get(key, default)


def update_item(old_item, updated_values):
    """
    Function that will update the values for a given task.
    :param old_item: the original item
    :param updated_values: the updated values
    :return: the updated item
    """

    return {
        'title': join_kv(updated_values, old_item, 'title', ''),
        'body': join_kv(updated_values, old_item, 'body', ''),
        'created': join_kv(updated_values, old_item, 'created', 0),
        'due': join_kv(updated_values, old_item, 'due', 0),
        'state': join_kv(updated_values, old_item, 'state', 'open')
    }


def convert_item(doc):
    """
    Function that takes an item as a dict (db document) and converts it in the equivalent api dict.
    :param doc: the db document.
    :return: the api equivalent dict
    """

    item_id = str(doc['_id'])
    ret = update_or_init(doc)
    url = '%s/%s' % (config.api_url_start, item_id)
    ret['task_id'] = item_id
    ret['_links'] = [
        build_link(rel='self', href=url, method=Methods.GET),
        build_link(rel='update', href=url, method=Methods.POST, args=[]),
        build_link(rel='delete', href=url, method=Methods.DELETE),
    ]
    return ret


def convert_item_list(items_cursor):
    """
    function that takes a list of items and converts it to an equivalent api dict.
    :param items_cursor: a cursor to the db collection.
    :return: an equivalent api dict.
    """

    ret = []
    for doc in items_cursor:
        ret.append(convert_item(doc))

    return ret


def build_response(**kwargs):
    """
    Function that builds a response based the arguments given.
    :param kwargs:
        items_cursor - will prompt the function to fetch and build a list of items retrieved with
            the cursor
        item - alternatively, it can convert a single item given as argument
    :return: the http response based on the given item/items
    """

    if 'items_cursor' in kwargs and kwargs['items_cursor'] is not None:
        items = convert_item_list(kwargs['items_cursor'])
    else:
        if 'item' in kwargs and kwargs['item'] is not None:
            items = [convert_item(kwargs['item'])]
        else:
            items = []

    resp = {
        'status': kwargs.get('status', 'OK'),
        'status_code': kwargs.get('status_code', 200),
        'record_count': kwargs.get('count', len(items)),
        'data': [
            {
                'tasks': items,
                '_links': [
                    build_link(rel='self', href=config.api_url_start, method=Methods.GET),
                    build_link(rel='add', href=config.api_url_start, method=Methods.POST, args=[]),
                    build_link(rel='list', href='%s/list' % config.api_url_start, method=Methods.GET)
                ]
            }
        ]

    }
    return jsonify(resp), resp['status_code']


def get_404():
    """
    Return a 404 response.
    """

    return build_response(
            status='Not found.',
            status_code=404
    )


def get_400():
    """
    Return a 400 response.
    """

    return build_response(
            status='Bad request.',
            status_code=400
    )
