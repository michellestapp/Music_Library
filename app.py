from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv
from os import environ
from marshmallow import post_load, fields, ValidationError

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Models
class Music(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    artist = db.Column(db.String, nullable = False)
    album = db.Column(db.String)
    release_date = db.Column(db.Date)
    genre = db.Column(db.String)



# Schemas
class MusicSchema(ma.Schema):
    id = fields.Integer(primary_key = True)
    title = fields.String(required = True)
    artist = fields.String(required=True)
    album = fields.String()
    release_date = fields.Date()
    genre = fields.String()

    @post_load
    def create(self, data, **kwargs):
        return Music(**data)

    class Meta:
        fields = ("id","title","artist","album","release_date","genre")
    
music_schema = MusicSchema()
musics_schema = MusicSchema(many = True)


# Resources



# Routes
