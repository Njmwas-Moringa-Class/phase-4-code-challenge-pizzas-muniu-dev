#!/usr/bin/env python3

from models import db, Restaurant, Pizza, RestaurantPizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return '<h1>Welcome to Code Challenge</h1>'


@app.route('/restaurants', methods=['GET'])
def fetch_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants]), 200, {'Content-Type': 'application/json'}


@app.route('/restaurants/<int:id>', methods=['GET'])
def fetch_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        return jsonify(restaurant.to_dict(include_pizzas=True))
    else:
        return jsonify({"error": "Restaurant not found"}), 404


@app.route('/restaurants/<int:id>', methods=['DELETE'])
def remove_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
        return jsonify({"error": "Restaurant not found"}), 404


@app.route('/pizzas', methods=['GET'])
def fetch_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])


@app.route('/restaurant_pizzas', methods=['POST'])
def add_restaurant_pizza():
    try:
        new_restaurant_pizza = RestaurantPizza(
            price=request.json.get('price'),
            pizza_id=request.json.get('pizza_id'),
            restaurant_id=request.json.get('restaurant_id'),
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()

        # Retrieve the associated pizza and restaurant
        pizza = db.session.get(Pizza, new_restaurant_pizza.pizza_id)
        restaurant = db.session.get(Restaurant, new_restaurant_pizza.restaurant_id)

        return jsonify({
            'id': new_restaurant_pizza.id,
            'price': new_restaurant_pizza.price,
            'pizza': pizza.to_dict(),
            'pizza_id': new_restaurant_pizza.pizza_id,
            'restaurant': restaurant.to_dict(),
            'restaurant_id': new_restaurant_pizza.restaurant_id
        }), 201
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400



if __name__ == '__main__':
    app.run(port=5555, debug=True)
