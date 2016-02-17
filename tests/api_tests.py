import unittest

from flask import json
from pymongo import MongoClient

from tests.helper_functions import CustomApiTestCase, get_mock_item_list
from web_api.routes import app


class ApiTestCase(CustomApiTestCase):
    def __init__(self, *args, **kwargs):
        self.maxDiff = None
        super().__init__(*args, **kwargs)

    def setUp(self):
        """
        Setup for the test environment.
        """

        app.config['api.vars'].db_name = 'test_tasks_db'
        self.config = app.config['api.vars']
        self.app = app.test_client()

    def test_add_new_item(self):
        """
        Test for adding a new task.
        """

        # add the new task
        mock_data = {
            'title': 'Task 1',
            'body': 'Body of task 1.',
            'status': 'closed'
        }
        res = self.post(self.config.api_url_start, mock_data)
        self.assertEqual(res.status_code, 200)

        # test if the data returned matches
        item = json.loads(res.data)
        mock_data['id'] = str(item['data'][0]['tasks'][0]['task_id'])
        self.assertEqual(item, get_mock_item_list([mock_data]))

    def test_update_item(self):
        """
        Test for task updating.
        """

        # add the test task
        mock_data = {
            'title': 'Task 1',
            'body': 'Body of task 1.',
            'status': 'closed'
        }
        res = self.post(self.config.api_url_start, mock_data)
        self.assertEqual(res.status_code, 200)

        # update the task
        item = json.loads(res.data)
        mock_data['id'] = str(item['data'][0]['tasks'][0]['task_id'])

        res = self.post(self.config.api_url_item % mock_data['id'], {
            'title': 'Modified title.',
            'body': 'Modified body.'
        })

        self.assertEqual(res.status_code, 200)
        item = json.loads(res.data)

        # check the return data
        mock_data['title'] = 'Modified title.'
        mock_data['body'] = 'Modified body.'
        self.assertEqual(item, get_mock_item_list([mock_data]))

    def test_delete_item(self):
        """
        Test for task deletion.
        """

        # add the test task
        mock_data = {
            'title': 'Task 1',
            'body': 'Body of task 1.',
            'status': 'closed'
        }
        res = self.post(self.config.api_url_start, mock_data)
        self.assertEqual(res.status_code, 200)

        # fetch the id
        item = json.loads(res.data)
        mock_data['id'] = str(item['data'][0]['tasks'][0]['task_id'])

        # delete the task
        self.delete(self.config.api_url_item % mock_data['id'])

        # check it doesn't exist on the item fetching endpoint
        res = self.get(self.config.api_url_item % mock_data['id'])
        self.assertEqual(res.status_code, 404)

        # check there are no items in item list fetching endpoint
        res = self.get(self.config.api_url_start)
        self.assertEqual(res.status_code, 200)

        item = json.loads(res.data)
        self.assertEqual(item['record_count'], 0)

    def test_get_all(self):
        """
        Test for item list retrieval.
        """

        # add the test tasks
        mock_data1 = {
            'title': 'Task 1',
            'body': 'Body of task 1.',
            'status': 'closed'
        }

        res = self.post('%s' % self.config.api_url_start, mock_data1)
        self.assertEqual(res.status_code, 200)

        # fetch the id of the first task
        item = json.loads(res.data)
        mock_data1['id'] = str(item['data'][0]['tasks'][0]['task_id'])

        mock_data2 = {
            'title': 'Task 2',
            'body': 'Body of task 2.',
            'status': 'ongoing'
        }

        res = self.post(self.config.api_url_start, mock_data2)
        self.assertEqual(res.status_code, 200)

        # fetch the id of the 2nd task
        item = json.loads(res.data)
        mock_data2['id'] = str(item['data'][0]['tasks'][0]['task_id'])

        res = self.get('%s/list' % self.config.api_url_start)
        item = json.loads(res.data)

        # check the item list to correctly contain the two tasks
        self.assertEqual(item['record_count'], 2)
        self.assertEqual(item, get_mock_item_list([mock_data1, mock_data2]))

    def test_get_item(self):
        """
        Test for item retrieval.
        """

        # add the test task
        mock_data = {
            'title': 'Task 1',
            'body': 'Body of task 1.',
            'status': 'closed'
        }

        res = self.post(self.config.api_url_start, mock_data)
        self.assertEqual(res.status_code, 200)

        # get the task id
        item = json.loads(res.data)
        mock_data['id'] = str(item['data'][0]['tasks'][0]['task_id'])

        # check the item is properly fetched through the item endpoint
        res = self.get(self.config.api_url_item % mock_data['id'], )

        item = json.loads(res.data)
        self.assertEqual(item, get_mock_item_list([mock_data]))

    def tearDown(self):
        """
        Tear down test environment.
        """

        # delete database
        MongoClient().drop_database(self.config.db_name)


# run from project root directory with:
# python -m unittest tests.api_tests
if __name__ == '__main__':
    unittest.main()
