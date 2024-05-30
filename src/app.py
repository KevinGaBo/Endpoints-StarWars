"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Planets, Favorite_character, Favorite_planet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)



@app.route('/user', methods=['GET'])
def get_user():
    user = User.query.all()
    serialized_usr = [usr.serialize() for usr in user]

    return jsonify(serialized_usr), 200

@app.route('/characters', methods=['GET'])
def get_characters():
    characters = Characters.query.all()
    serialized_character = [character.serialize() for character in characters]

    return jsonify(serialized_character), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()
    serialized_planet = [planet.serialize() for planet in planets]

    return jsonify(serialized_planet), 200

@app.route('/characters/<int:characters_id>', methods=['GET'])
def get_character(characters_id):
    characters = Characters.query.get(characters_id)
    if characters:
        serialized_character = characters.serialize()
        return jsonify(serialized_character), 200
    else:
        return jsonify({"msg" : "person not found"}), 400
    
@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_planet(planets_id):
    planets = Planets.query.get(planets_id)
    if planets:
        serialized_planet = planets.serialize()
        return jsonify(serialized_planet), 200
    else:
        return jsonify({"msg" : "person not found"}), 400
    

@app.route('/favorite/<int:favorite_type_id>', methods=['POST'])
def add_favorite(favorite_type_id):
    data = request.json 
    user_id = data['user_id']
    #1 para personajes y 2 para planetas

    if favorite_type_id == 1: 
        character_id = data['character_id']
        new_character_favorite = Favorite_character(
            user_id = user_id, character_id = character_id
        )
        db.session.add(new_character_favorite)
        db.session.commit()
        return jsonify(data), 200
    if favorite_type_id == 2:
        planet_id = data['planet_id']
        new_planet_favorite = Favorite_planet(
            user_id = user_id, planet_id = planet_id
        )
        db.session.add(new_planet_favorite)
        db.session.commit()
        return jsonify(data), 200
        
    return {}, 400


@app.route('/favorite/<int:favorite_type_id>', methods=['DELETE'])
def remove_favorite(favorite_type_id):
    data = request.json
    user_id = data['user_id']
    # 1 para personajes y 2 para planetas

    if favorite_type_id == 1:
        character_id = data['character_id']
        remove_fav_character = Favorite_character.query.filter_by(user_id=user_id, character_id=character_id).first()
        if remove_fav_character:
            db.session.delete(remove_fav_character)
            db.session.commit()
            return jsonify({"msg": "Favorite character removed"}), 200
    elif favorite_type_id == 2:
        planet_id = data['planet_id']
        remove_fav_planet = Favorite_planet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
        if remove_fav_planet:
            db.session.delete(remove_fav_planet)
            db.session.commit()
            return jsonify({"msg": "Favorite planet removed"}), 200      
    return jsonify({"msg": "Favorite not found"}), 404


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
