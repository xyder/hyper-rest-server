from flask import jsonify
import config
from web_api.api_lib import Page, Payload, Item


def convert_item(doc):
    """
    Function that takes an item as a dict (db document) and converts it in the equivalent api item.
    :param doc: the db document.
    :return: the api item
    """

    item_id = str(doc['_id'])
    return Item(
        task_id=item_id,
        title=doc.get('title', ''),
        body=doc.get('body', ''),
        created=doc.get('created', 0),
        due=doc.get('due', 0),
        state=doc.get('state', 'open'),
        url='%s/%s' % (config.api_url_start, item_id)
    )


def build_response(**kwargs):
    """
    Function that builds a response based the arguments given.
    :param kwargs:
        items_cursor - will prompt the function to fetch and build a list of items retrieved with
            the cursor
        item - alternatively, it can convert a single item given as argument
    :return: the http response based on the given item/items
    """

    items_cursor = kwargs.get('items_cursor')
    item = kwargs.get('item')
    items = []

    if items_cursor:
        for item in items_cursor:
            items.append(convert_item(item))
    elif item:
        if isinstance(item, Item):
            items = [item]
        else:
            items = [convert_item(item)]

    page = Page(status=kwargs.get('status', 'OK'),
                status_code=kwargs.get('status_code', 200),
                record_count=kwargs.get('count', len(items)),
                payloads=[Payload(items=items, url=config.api_url_start)])

    return jsonify(page.to_dict()), page.status_code

