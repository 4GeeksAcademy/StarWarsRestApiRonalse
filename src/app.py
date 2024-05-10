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
from models import db, User, Favorite, People, Planets
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
def get_users():
    users= User.query.all()
    all_users = list(map(lambda item: item.serialize(), users))
    return jsonify(all_users), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    Pick_user = User.query.filter_by(id=user_id).first()
    if Pick_user is None:
         raise APIException('User does not exist', status_code=404)
    return jsonify(Pick_user.serialize()), 200

@app.route('/user', methods=['POST'])
def create_user():
    request_body_user = request.get_json()
    new_user = User(username=request_body_user["username"], email=request_body_user["email"], password=request_body_user["password"], is_active=request_body_user["is_active"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify(request_body_user), 200

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    request_body_user = request.get_json()
    Pick_user = User.query.get(user_id)
    if Pick_user is None:
        raise APIException('User not found', status_code=404)
    if "username" in request_body_user:
        Pick_user.username = request_body_user["username"]
    if "password" in request_body_user:
        Pick_user.password = request_body_user["password"]
    if "email" in request_body_user:
        Pick_user.email = request_body_user["email"]
    db.session.commit()
    return jsonify(request_body_user), 200

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    chosen_user = User.query.get(user_id)
    if chosen_user is None:
        raise APIException('User not found', status_code=404)
    db.session.delete(chosen_user)
    db.session.commit()
    return jsonify("User successfully deleted"), 200

# favorites methods

@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        raise APIException('User not found', status_code=404)
    user_favorites = Favorite.query.filter_by(user_id=user_id).all()
    if not user_favorites:
        raise APIException('User has no favorites', status_code=404)
    serialized_favorites = [favorite.serialize() for favorite in user_favorites]
    return jsonify(serialized_favorites), 200

@app.route('/user/<int:user_id>/favorites/people/<int:favoritePersonId>', methods=['POST'])
def add_people_favorite(user_id, favoritePersonId):
    user = User.query.get(user_id)
    if not user:
        raise APIException('User not found', status_code=404)
    people = People.query.get(favoritePersonId)
    if not people:
        raise APIException('Character not found', status_code=404)
    if Favorite.query.filter_by(user_id=user_id, favoritePersonId=favoritePersonId).first():
        raise APIException('The character is already on the favorites list', status_code=400)
    favorite = Favorite(user_id=user_id, favoritePersonId=favoritePersonId)
    db.session.add(favorite)
    db.session.commit()
    return jsonify("Character added to favorites successfully"), 200

@app.route('/user/<int:user_id>/favorites/people/<int:favoritePersonId>', methods=['DELETE'])
def delete_people_favorite(user_id, favoritePersonId):
    favorite = Favorite.query.filter_by(user_id=user_id, favoritePersonId=favoritePersonId).first()
    if not favorite:
        raise APIException('Favorite not found', status_code=404)
    db.session.delete(favorite)
    db.session.commit()
    return jsonify("Favorite successfully deleted"), 200

@app.route('/user/<int:user_id>/favorites/planets/<int:favoritePlanetId>', methods=['POST'])
def add_planet_favorite(user_id, favoritePlanetId):
    user = User.query.get(user_id)
    if not user:
        raise APIException('User not found', status_code=404)
    planet = Planets.query.get(favoritePlanetId)
    if not planet:
        raise APIException('Planet not found', status_code=404)
    if Favorite.query.filter_by(user_id=user_id, favoritePlanetId=favoritePlanetId).first():
        raise APIException('The planet is already on the favorites list', status_code=400)
    favorite = Favorite(user_id=user_id, favoritePlanetId=favoritePlanetId)
    db.session.add(favorite)
    db.session.commit()
    return jsonify("Planet added to favorites successfully"), 200

@app.route('/user/<int:user_id>/favorites/planets/<int:favoritePlanetId>', methods=['DELETE'])
def delete_planet_favorite(user_id, favoritePlanetId):
    favorite = Favorite.query.filter_by(user_id=user_id, favoritePlanetId=favoritePlanetId).first()
    if not favorite:
        raise APIException('Favorite not found', status_code=404)
    db.session.delete(favorite)
    db.session.commit()
    return jsonify("Favorite successfully deleted"), 200
    
# people methods

@app.route('/people', methods=['GET'])
def get_people():
    People_query = People.query.all()
    results = list(map(lambda item: item.serialize(),People_query))
    if results == []:
         raise APIException('There are no people', status_code=404)
    return jsonify(results), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def people(people_id):
    People_query = People.query.filter_by(id= people_id).first()
    if People_query is None:
         raise APIException('The character does not exist', status_code=404)
    return jsonify(People_query.serialize()), 200

@app.route('/people', methods=['POST'])
def create_people():
    request_body_user = request.get_json()
    new_people = People(height=request_body_user["height"], mass=request_body_user["mass"], hair_color=request_body_user["hair_color"], birth_year=request_body_user["birth_year"], gender=request_body_user["gender"], name=request_body_user["name"])
    db.session.add(new_people)
    db.session.commit()
    return jsonify(request_body_user), 200

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_people(people_id):
    chosen_people = People.query.get(people_id)
    if chosen_people is None:
        raise APIException('Character not found', status_code=404)
    db.session.delete(chosen_people)
    db.session.commit()
    return jsonify("Character successfully deleted"), 200

# planets methods

@app.route('/planets', methods=['GET'])
def get_planets():
    planets_query = Planets.query.all()
    results = list(map(lambda item: item.serialize(),planets_query))
    if results == []:
         raise APIException('There are no planets', status_code=404)
    return jsonify(results), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def planet(planet_id):
    planet_query = Planets.query.filter_by(id= planet_id).first()
    if planet_query is None:
         raise APIException('The planet does not exist', status_code=404)
    return jsonify(planet_query.serialize()), 200

@app.route('/planets', methods=['POST'])
def create_planet():
    request_body_user = request.get_json()
    new_planet = Planets(diameter=request_body_user["diameter"], rotation_period=request_body_user["rotation_period"], orbital_period=request_body_user["orbital_period"], climate=request_body_user["climate"], terrain=request_body_user["terrain"], surface_water=request_body_user["surface_water"], population=request_body_user["population"], name=request_body_user["name"])
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(request_body_user), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    chosen_planet = Planets.query.get(planet_id)
    if chosen_planet is None:
        raise APIException('Planet not found', status_code=404)
    db.session.delete(chosen_planet)
    db.session.commit()
    return jsonify("Planet successfully deleted"), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
