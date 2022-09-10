import json
import functools
from bson import json_util
from datetime import datetime, date

from flask_pymongo import PyMongo
from flask import (
    Blueprint, request, current_app, jsonify
)

bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@bp.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        mongodb_client = PyMongo(current_app, uri="mongodb://localhost:27017/library")
        db = mongodb_client.db


        book_name = request.form.get('book_name')
        person_name = request.form.get('person')
        issue_date = request.form.get('issue_date')
        return_date = request.form.get('return_date')

        book_id = db.books.find_one({"name": {"$regex" : "(?i)" + book_name}}, {"_id": 1})
        book_rent = db.books.find_one({"name": {"$regex" : "(?i)" + book_name}}, {"rent_per_day": 1})


        if issue_date is not None:
            db.transactions.insert_one({
                "book_id": book_id["_id"],
                "person": person_name,
                "issue_date" : issue_date
            })

            return jsonify({
                "message": "Book issued successfully"
            })

        else:
            db.transactions.insert_one({
                "book_id": book_id["_id"],
                "person": person_name,
                "return_date" : return_date
            })

            issue_date = db.transactions.find_one({"book_id": book_id["_id"]}, {"issue_date": 1})
            print(issue_date["issue_date"])
            print(return_date)
            rent = book_rent["rent_per_day"] * (datetime.fromisoformat(return_date[:-1]) - datetime.fromisoformat(issue_date['issue_date'][:-1])).days

            return jsonify({
                "message": "Book returned successfully",
                "rent": rent
            })

    elif request.method == 'GET':
        return "hello there"