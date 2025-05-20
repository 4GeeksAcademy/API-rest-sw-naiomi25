"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os


from sqlalchemy import select

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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

    stm = select(User)
    data = db.session.execute(stm).scalars().all()
    data = list(map(lambda item: item.serialize(), data))

    if data:
        return jsonify(data), 200
    else:
        return jsonify({'error': 'user no encontrado'}), 404


@app.route('/people')
def get_people():

    stm = select(People)
    get_people = db.session.execute(stm).scalars().all()
    get_people = list(map(lambda person: person.serialize(), get_people))

    if get_people:
        return jsonify(get_people), 200
    else:
        return jsonify({
            'msg': 'Aun no hay personajes'
        })


@app.route('/planets')
def get_planets():

    stm = select(Planets)
    get_planets = db.session.execute(stm).scalars().all()
    get_planets = list(map(lambda planet: planet.serialize(), get_planets))

    if get_planets:
        return jsonify(get_planets)
    else:
        return jsonify({
            'msg': 'Aún no hay planetas'
        })


@app.route('/people/<int:people_id>')
def get_people_id(people_id):
    stm = select(People).where(People.id == people_id)
    get_id_people = db.session.execute(stm).scalar_one_or_none()

    if get_id_people:

        return jsonify(get_id_people.serialize()), 200

    else:
        return  jsonify({ 'msg': ' no hay coincidencias'  }), 400
           
        

@app.route('/planet/<int:planet_id>')
def get_panet_id(planet_id):

    stm = select(Planets).where(Planets.id == planet_id)
    get_panet_id = db.session.execute(stm).scalar_one_or_none()

    if get_panet_id:
        return jsonify(get_panet_id.serialize()), 200
    else:
        return jsonify({
            'msg': 'no hay ninguna conincidencia'
        }), 400


@app.route('/users/<int:user_id>/favorites')
def user_favorites(user_id):

    stm = select(User).where(User.id == user_id)
    user = db.session.execute(stm).scalar_one_or_none()

    if not user:

        return jsonify({'msg': 'No existe ningún usuario con ese id'}), 404

    favorite_planets = list(
        map(lambda item: item.serialize(), user.favorites_planet))
    favorite_people = list(
        map(lambda item: item.serialize(), user.favorites_people))

    favoritos = {

        "planets": favorite_planets,
        "people": favorite_people

    }

    return jsonify(favoritos), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST','DELETE'])
def add_planet_favorite(planet_id):

    body = request.get_json(silent=True)

    if body is None:
        return jsonify({'msg': 'falta el id para encontrar al usuario'}), 400

    user_id = body.get('user_id')

    if user_id is None:
        return jsonify({'msg': 'Ususario no encontrado'}), 404

    stm = select(User).where(User.id == user_id)
    user = db.session.execute(stm).scalar_one_or_none()
    if user is None:
        return jsonify({'msg': 'Usuario no regristrado en la base de datos'}),404

    stm = select(Planets).where(planet_id == Planets.id)
    planet = db.session.execute(stm).scalar_one_or_none()

    if planet is None:
        return jsonify({'msg': 'Planeta no encontrado'}), 404
    
    if request.method == 'POST':
        
        if planet not in user.favorites_planet:

            user.favorites_planet.append(planet)
            db.session.commit()

            return jsonify({'msg': 'Planeta añadido a favoritos'}), 200
        else:
            return jsonify({'msg': 'Planeta ya se encuentra en favoritos'}), 200
    else:

        if planet  in user.favorites_planet:

            user.favorites_planet.remove(planet)
            db.session.commit()
            return jsonify({'msg': 'Planeta eliminado de favoritos'}), 200
        else:
            return jsonify({'msg': 'Planeta no estaba en favoritos'}), 404
       

@app.route('/favorite/people/<int:people_id>',methods = ['POST','DELETE'])
def add_people_favorite(people_id):

    body = request.get_json()
    user_id = body.get ( 'user_id')


    if body is None or user_id is None:
        return jsonify({'msg': 'Falta información del usuario'}), 400
    
    stm = select(User).where ( user_id == User.id)
    user = db.session.execute(stm).scalar_one_or_none()

    if user is None :
         return jsonify({'msg': 'No existe ese usuario'}), 404

    stm = select(People).where(people_id == People.id)
    people = db.session.execute(stm).scalar_one_or_none()

    if people is None :
         return jsonify({'msg': 'No existe ese personaje en la base de datos'}), 404
    
    if request.method == 'POST':
    
        if people not in user.favorites_people:

            user.favorites_people.append(people)
            db.session.commit()
            return jsonify({'msg': 'Personaje añadido correctamente'}), 200
        else:
            return jsonify({'msg': 'El personaje ya está en favortos'}), 200
        
    else:

        if people  in user.favorites_people:

            user.favorites_people.remove(people)
            db.session.commit()
            return jsonify({'msg': 'Personaje eliminado de favoritos'}), 200
        else:
            return jsonify({'msg': 'El personaje no estaba en favoritos'}), 404


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
