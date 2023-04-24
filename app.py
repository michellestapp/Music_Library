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
class Song(db.Model):
    song_id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255), nullable = False)
    artist = db.Column(db.String(255), nullable = False)
    album = db.Column(db.String(255))
    release_date = db.Column(db.Date)
    genre = db.Column(db.String(255))

    def __repr__(self):
        return f'{self.title} {self.artist} {self.album} {self.release_date} {self.genre}'

# Schemas
class SongSchema(ma.Schema):
    song_id = fields.Integer(primary_key = True)
    title = fields.String(required = True)
    artist = fields.String(required=True)
    album = fields.String()
    release_date = fields.Date()
    genre = fields.String()

    @post_load
    def create(self, data, **kwargs):
        return Song(**data)

    class Meta:
        fields = ("id","title","artist","album","release_date","genre")
    
song_schema = SongSchema()
songs_schema = SongSchema(many = True)


# Resources
class SongListResources(Resource):

    def get(self):
        all_songs = Song.query.all()
        return songs_schema.dump(all_songs),200
    
    def post(self):
        form_data = request.get_json()
        try:
            new_song = song_schema.load(form_data)
            db.session.add(new_song)
            db.session.commit()
            return song_schema.dump(new_song), 201
        except ValidationError as err:
            return err.messages,400

class SongResources(Resource):
    def get(self,song_id):
        song_from_db = Song.query.get_or_404(song_id)
        return song_schema.dump(song_from_db), 

# Routes

api.add_resource(SongListResources, '/api/songs')
api.add_resource(SongResources, '/api/songs/<song_id>')
