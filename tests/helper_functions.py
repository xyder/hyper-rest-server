import unittest

from flask import json

import config


def get_mock_task(item):
    """
    Function that builds a mock task based on the given arguments.
    :param item: item values to customize this mock item.
    :return: the mock item.
    """

    return {
        '_links': [
            {
                'href': config.api_url_item % item['id'],
                'method': 'GET',
                'rel': 'self'
            },
            {
                'args': [],
                'href': config.api_url_item % item['id'],
                'method': 'POST',
                'rel': 'update'
            },
            {
                'href': config.api_url_item % item['id'],
                'method': 'DELETE',
                'rel': 'delete'
            }
        ],
        'body': item.get('body', ''),
        'created': item.get('created', 0),
        'due': item.get('due', 0),
        'state': item.get('state', 'open'),
        'task_id': item['id'],
        'title': item.get('title', '')
    }


def get_mock_item_list(items):
    """
    Function that builds a mock item list based on the given items.
    :param items: the items used to customize the mock item list.
    :return: the mock item list.
    """

    ret = {
        'data': [
            {
                '_links': [
                    {
                        'href': config.api_url_start,
                        'method': 'GET',
                        'rel': 'self'
                    },
                    {
                        'args': [],
                        'href': config.api_url_start,
                        'method': 'POST',
                        'rel': 'add'
                    },
                    {
                        'href': '%s/list' % config.api_url_start,
                        'method': 'GET',
                        'rel': 'list'
                    }
                ],
                'tasks': []
            }
        ],
        'record_count': len(items),
        'status': 'OK',
        'status_code': 200
    }

    for item in items:
        ret['data'][0]['tasks'].append(get_mock_task(item))

    return ret


class CustomApiTestCase(unittest.TestCase):
    """
    Class that extends the TestCase with functions required for building test cases.
    """

    def get(self, route):
        """
        Sends an HTTP GET request.
        :param route: the url used.
        :return: the received result.
        """

        return self.app.get(route, follow_redirects=True)

    def post(self, route, data):
        """
        Sends an HTTP POST request.
        :param route: the url used.
        :param data: the data to be sent.
        :return: the received result.
        """

        return self.app.post(
                route,
                data=json.dumps(data),
                content_type='application/json',
                follow_redirects=True
        )

    def delete(self, route):
        """
        Sends an HTTP DELETE request.
        :param route: the url used.
        :return: the received result.
        """

        return self.app.delete(route, follow_redirects=True)
