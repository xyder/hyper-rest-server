from pymongo import MongoClient
from flask import Flask

import config
from web_api.response_builders import build_response

app = Flask(__name__)


@app.route('/api/v%s/tasks' % config.api_version, methods=['GET'])
def get_tasks():
    client = MongoClient()
    db = client.tasks_db
    return build_response(
        items_cursor=db.tasks.find()
    )
