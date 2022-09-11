import json
import os
from bson import json_util

import pymongo
# from flask_pymongo import PyMongo
from flask import (
    Blueprint, request, jsonify
)

bp = Blueprint('books', __name__, url_prefix='/books')

mongodb_client = pymongo.MongoClient(f"mongodb+srv://satyamrs00:{os.environ.get('DB_PASSWORD')}@scouto-library.cgqh2we.mongodb.net/?retryWrites=true&w=majority")
db = mongodb_client.library

@bp.route('/', methods=['GET'])
def index():
    name = request.args.get('name')
    from_rent = request.args.get('from_rent')
    to_rent = request.args.get('to_rent')
    category = request.args.get('category')

    if name is not None:
        if category is not None and from_rent is not None and to_rent is not None:
            books = db.books.find({
                "name" : {"$regex" : ".*(?i)" + name + ".*"}, 
                'category': {'$regex': '(?i)' + category}, 
                "rent_per_day": {'$gte' : int(from_rent), '$lte': int(to_rent)}
            }, 
            {"_id" : 0})
        else:
            books = db.books.find({"name" : {"$regex" : ".*(?i)" + name + ".*"}}, {"_id" : 0})
    elif from_rent is not None and to_rent is not None:
        books = db.books.find({"rent_per_day": {'$gte' : int(from_rent), '$lte': int(to_rent)}}, {"_id" : 0})
    else:
        return jsonify({
            "message": "Please provide a name or rent range"
        })

    return json.loads(json_util.dumps(books))