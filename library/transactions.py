import json
import functools
from bson import json_util
from datetime import datetime
from dateutil import parser

from flask_pymongo import PyMongo
from flask import (
    Blueprint, request, current_app, jsonify
)

bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@bp.route('/', methods=['POST', 'GET'])
def index():
    mongodb_client = PyMongo(current_app, uri="mongodb://localhost:27017/library")
    db = mongodb_client.db

    if request.method == 'POST':
        book_name = request.form.get('book')
        person_name = request.form.get('person')
        issue_date = request.form.get('issue_date')
        return_date = request.form.get('return_date')

        book = db.books.find_one({"name": {"$regex" : "(?i)" + book_name}})

        if issue_date is not None and return_date is None:
            db.transactions.insert_one({
                "book_id": book["_id"],
                "person": person_name,
                "issue_date" : datetime.fromisoformat(issue_date[:-1])
            })

            return jsonify({
                "message": "Book issued successfully"
            })

        elif issue_date is None and return_date is not None:
            db.transactions.update_one({
                "book_id": book["_id"],
                "person": {'$regex': '(?i)' + person_name},
                'issue_date': {'$type': 9},
                "return_date" : {'$exists': False}
            },
            {
                '$set': {
                    "return_date": datetime.fromisoformat(return_date[:-1])
                }
            })

            issue_date = db.transactions.find_one({"book_id": book["_id"]}, {"issue_date": 1})
            rent = book["rent_per_day"] * (datetime.fromisoformat(return_date[:-1]) - issue_date['issue_date']).days
            
            return jsonify({
                "message": "Book returned successfully",
                "rent": rent
            })
        else:
            return jsonify({
                "message": "Please provide either issue date or return date"
            })

    elif request.method == 'GET':
        book_name = request.args.get('book')
        person_name = request.args.get('person')
        from_date = request.args.get('from')
        to_date = request.args.get('to')

        if book_name is not None:
            book = db.books.find_one({"name": {"$regex" : "(?i)" + book_name}})

            transactions = db.transactions.find({"book_id": book['_id'], "issue_date": {"$type": 9}}, {"_id": 0})
            transactions_active = db.transactions.find({"book_id": book['_id'], "issue_date": {"$type": 9}, 'return_date': {'$exists': False}}, {"_id": 0})
            transactions_completed = db.transactions.find({"book_id": book['_id'], "issue_date": {"$type": 9}, 'return_date': {'$type': 9}}, {"_id": 0})

            renters = [transaction['person'] for transaction in transactions]
            active_renters = [transaction['person'] for transaction in transactions_active]

            total_collected = 0
            for transaction in transactions_completed:
                total_collected += (transaction['return_date'] - transaction['issue_date']).days * book['rent_per_day']

            return jsonify(renters=renters, renterCount=len(renters), activeRenters=active_renters, activeRenterCount=len(active_renters), totalRentCollected=total_collected)

        elif person_name is not None:
            books = db.transactions.find({
                "person": {
                    "$regex" : "(?i)" + person_name
                }
            }, 
            {
                "_id": 0, 
                "book_id": 1
            })
            transactions = db.books.find({
                "_id": {
                    "$in": [book["book_id"] for book in books]
                }
            }, 
            {"_id": 0})
            
        elif from_date is not None and to_date is not None:
            transactions = db.transactions.aggregate([
                {'$match': {
                    "issue_date": { 
                        '$gt': parser.parse(from_date), 
                        '$lt': parser.parse(to_date) 
                    }
                }},
                {
                    "$lookup":{
                        "from": "books",
                        "localField": "book_id",
                        "foreignField": "_id",
                        "pipeline": [
                            { "$project": { "_id": 0 }}
                        ],
                        "as": "book"
                    }
                },
                {'$project': {
                    '_id' : 0,
                    'book_id' : 0
                }},
                {
                    '$unwind': {
                        'path': '$book'                        
                    }
                }
            ])
        else:
            return jsonify({
                "message": "Please provide either book name or person name or date range"
            })
        
        return json.loads(json_util.dumps(transactions))