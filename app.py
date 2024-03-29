from flask import Flask, request, json
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
    run_time = db.Column(db.Integer)
    song_file = db.Column(db.LargeBinary)

    def __repr__(self):
        return f' {self.song_id} {self.title} {self.artist} {self.album} {self.release_date} {self.genre}'

# Schemas
class SongSchema(ma.Schema):
    song_id = fields.Integer(primary_key = True)
    title = fields.String(required = True)
    artist = fields.String(required=True)
    album = fields.String()
    release_date = fields.Date()
    genre = fields.String()
    run_time = fields.Integer()
    song_file = fields.Raw() 

    @post_load
    def create(self, data, **kwargs):
        return Song(**data)

    class Meta:
        fields = ("song_id","title","artist","album","release_date","genre","run_time", "song_file")
    
song_schema = SongSchema()
songs_schema = SongSchema(many = True)


# Resources
class SongListResources(Resource):

    def get(self):
        custom_response = {}
        total_run_time = 0
        total_run_time_seconds = 0

        all_songs = Song.query.all()

        for item in all_songs:
            total_run_time += item.run_time
            
        # total_run_time = round(total_run_time/60,2)
        print(total_run_time)

        total_run_time_formatted = f"{total_run_time // 60} min {total_run_time % 60} sec"

        custom_response = {
            "songs": songs_schema.dump(all_songs),
            "total_run_time_formatted": total_run_time_formatted  
        }


        return custom_response,200
    
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
        return song_schema.dump(song_from_db), 200
    
    def put(self, song_id):
        song_from_db = Song.query.get_or_404(song_id)

        if 'title' in request.json:
            song_from_db.title = request.json['title']
        if 'artist' in request.json:
            song_from_db.artist = request.json['artist']
        if 'album' in request.json:
            song_from_db.album = request.json['album']
        if 'release_date' in request.json:
            song_from_db.release_date = request.json['release_date']
        if 'genre' in request.json:
            song_from_db.genre = request.json['genre']
        if 'run_time' in request.json:
            song_from_db.run_time = request.json['run_time']

        db.session.commit()
        return song_schema.dump(song_id), 200
    
    def delete(self,song_id):
        song_from_db = Song.query.get_or_404(song_id)
        db.session.delete(song_from_db)
        db.session.commit()
        return '',204
    
    def post(self):
        form_data = request.form 
        song_data = json.loads(form_data['data'])

        if 'song_file' not in request.files:
            return {"message": "No file part"}, 400

        file = request.files['song_file']
        try:
            new_song = song_schema.load(song_data)
            new_song.song_file = file.read()
            db.session.add(new_song)
            db.session.commit()
            return song_schema.dump(new_song), 201
        except ValidationError as err:
            return err.messages, 400


# Routes

api.add_resource(SongListResources, '/api/songs')
api.add_resource(SongResources, '/api/songs/<song_id>')
