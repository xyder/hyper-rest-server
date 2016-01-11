from flask import jsonify
import config


class Methods:
    POST = 'POST'
    GET = 'GET'
    DELETE = 'DELETE'


def build_link(**kwargs):
    ret = {
        'rel': kwargs.get('rel', ''),
        'href': kwargs.get('href', ''),
        'method': kwargs.get('method', Methods.GET),
    }

    if 'args' in kwargs:
        ret['args'] = kwargs['args']

    return ret


def build_add_link():
    return build_link(
            rel='add',
            href=config.api_url_start,
            method=Methods.POST,
            args=[]
    )


def build_self_link(item_id=None):
    url = config.api_url_start + ('' if not item_id else '/%s' % item_id)
    return build_link(
            rel='self',
            href=url,
            method=Methods.GET
    )


def build_delete_link(item_id):
    return build_link(
            rel='delete',
            href='%s/%s' % (config.api_url_start, item_id),
            method=Methods.DELETE,
    )


def build_update_link(item_id):
    return build_link(
            rel='update',
            href='%s/%s' % (config.api_url_start, item_id),
            method=Methods.POST,
            args=[]
    )


def update_or_init(values):
    return {
        'title': values.get('title', ''),
        'body': values.get('body', ''),
        'created': values.get('created', 0),
        'due': values.get('due', 0),
        'state': values.get('state', 'open')
    }


def join_kv(dict1, dict2, key, default=None):
    return dict1.get(key) if key in dict1 else dict2.get(key, default)


def join_dicts(old_item, updated_values):
    return {
        'title': join_kv(updated_values, old_item, 'title', ''),
        'body': join_kv(updated_values, old_item, 'body', ''),
        'created': join_kv(updated_values, old_item, 'created', 0),
        'due': join_kv(updated_values, old_item, 'due', 0),
        'state': join_kv(updated_values, old_item, 'state', 'open')
    }


def convert_item_list(items_cursor):
    ret = []
    for doc in items_cursor:
        item_id = str(doc['_id'])
        item = {
            'task_id': item_id,
            'title': doc.get('title', ''),
            'body': doc.get('body', ''),
            'created': doc.get('created', 0),
            'due': doc.get('due', 0),
            'state': doc.get('state', 'open'),
            '_links': [
                build_self_link(item_id),
                build_update_link(item_id),
                build_delete_link(item_id)
            ]
        }
        ret.append(item)

    return ret


def build_response(**kwargs):
    if 'items_cursor' in kwargs and kwargs['items_cursor'] is not None:
        items = convert_item_list(kwargs['items_cursor'])
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
                    build_self_link(),
                    build_add_link()
                ]
            }
        ]

    }
    return jsonify(resp), resp['status_code']


def get_404():
    return build_response(
            status='Not found.',
            status_code=404
    )


def get_400():
    return build_response(
            status='Bad request.',
            status_code=400
    )
