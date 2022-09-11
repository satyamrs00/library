import os

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
    )

    # # connect to the database
    # app.config['MONGODB_SETTINGS'] = {
    #     'db': 'library',
    #     'host': 'localhost',
    #     'port': 27017
    # }
    # db = MongoEngine(app)
    # db.init_app(app)
    # 
    # # register models
    # class Book(db.Document):
    #     name = db.StringField()
    #     category = db.StringField()
    #     rent_per_day = db.IntField()

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import books
    app.register_blueprint(books.bp)

    from . import transactions
    app.register_blueprint(transactions.bp)
    
    return app