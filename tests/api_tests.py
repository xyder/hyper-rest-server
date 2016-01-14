import unittest

from flask import json
from pymongo import MongoClient

from tests.helper_functions import get_valid_item, CustomApiTestCase
from web_api.routes import app


class ApiTestCase(CustomApiTestCase):
    def setUp(self):
        app.config['api.vars'].db_name = 'test_tasks_db'
        self.config = app.config['api.vars']
        self.app = app.test_client()

    def test_add_new_item(self):
        test_data = {
            'title': 'Task 1',
            'body': 'Body of task 1.',
            'status': 'closed'
        }
        res = self.post(self.config.api_url_start, test_data)
        assert res.status_code is 200

        item = json.loads(res.data)

        test_data['id'] = str(item['data'][0]['tasks'][0]['task_id'])
        self.assertEqual(item, get_valid_item(test_data))

    def tearDown(self):
        # delete database
        MongoClient().drop_database(self.config.db_name)


# run from project root directory with:
# python -m unittest tests.api_tests
if __name__ == '__main__':
    unittest.main()
