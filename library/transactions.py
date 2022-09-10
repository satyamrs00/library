import json
import functools
from bson import json_util

from flask_pymongo import PyMongo
from flask import (
    Blueprint, request, current_app
)

bp = Blueprint('transactions', __name__, url_prefix='/transactions')

bp.route('/', methods=['POST', 'PUT'])
def index():
    if request.method == 'PUT':
        mongodb_client = PyMongo(current_app, uri="mongodb://localhost:27017/library")
        db = mongodb_client.db

        