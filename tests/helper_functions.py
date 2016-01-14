import unittest

from flask import json


def get_valid_item(item):
    return {
        "data": [
            {
                "_links": [
                    {
                        "href": "/api/v1/tasks",
                        "method": "GET",
                        "rel": "self"
                    },
                    {
                        "args": [],
                        "href": "/api/v1/tasks",
                        "method": "POST",
                        "rel": "add"
                    }
                ],
                "tasks": [
                    {
                        "_links": [
                            {
                                "href": "/api/v1/tasks/%s" % item['id'],
                                "method": "GET",
                                "rel": "self"
                            },
                            {
                                "args": [],
                                "href": "/api/v1/tasks/%s" % item['id'],
                                "method": "POST",
                                "rel": "update"
                            },
                            {
                                "href": "/api/v1/tasks/%s" % item['id'],
                                "method": "DELETE",
                                "rel": "delete"
                            }
                        ],
                        "body": item.get('body', ''),
                        "created": item.get('created', 0),
                        "due": item.get('due', 0),
                        "state": item.get('state', 'open'),
                        "task_id": item['id'],
                        "title": item.get('title', '')
                    }
                ]
            }
        ],
        "record_count": 1,
        "status": "OK",
        "status_code": 200
    }


class CustomApiTestCase(unittest.TestCase):
    def get(self, route):
        return self.app.get(route, follow_redirects=True)

    def post(self, route, data):
        return self.app.post(
                route,
                data=json.dumps(data),
                content_type='application/json',
                follow_redirects=True
        )

    def delete(self, route):
        return self.app.delete(route, follow_redirects=True)
