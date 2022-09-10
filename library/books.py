import json
import functools
from bson import json_util

from flask_pymongo import PyMongo
from flask import (
    Blueprint, request, current_app
)

bp = Blueprint('books', __name__, url_prefix='/books')

@bp.route('/', methods=['POST'])
def index():
    mongodb_client = PyMongo(current_app, uri="mongodb://localhost:27017/library")
    db = mongodb_client.db

    name = request.form.get('name')
    from_rent = request.form.get('from_rent')
    to_rent = request.form.get('to_rent')
    category = request.form.get('category')

    if name is not None:
        if category is not None:
            print(name, category)
            print("\n\n\n\n\\n\\n\n\\n\n\n\nhere")
            books = db.books.find({
                "name" : {"$regex" : ".*(?i)" + name + ".*"}, 
                'category': category, 
                "rent_per_day": {'$gte' : int(from_rent), '$lte': int(to_rent)}
            }, 
            {"_id" : 0})
        else:
            books = db.books.find({"name" : {"$regex" : ".*(?i)" + name + ".*"}}, {"_id" : 0})
    else:
        books = db.books.find({"rent_per_day": {'$gte' : int(from_rent), '$lte': int(to_rent)}}, {"_id" : 0})

    return json.loads(json_util.dumps(books))

