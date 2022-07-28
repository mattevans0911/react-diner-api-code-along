from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_type=db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False, unique=True)
    price = db.Column(db.String, nullable=False)

    def __init__(self, title, price, menu_type):
        self.title = title
        self.price = price
        self.menu_type = menu_type


class FoodSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "price", "menu_type")

food_schema = FoodSchema()
multiple_food_schema = FoodSchema(many=True)

@app.route("/food/add", methods=["POST"])
def add_food():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")
    
    post_data = request.get_json()
    title = post_data.get("title")
    price = post_data.get("price")
    menu_type = post_data.get("menu-type")
    

    if title == None:
        return jsonify("Error: Data must have a 'title' key")
    if price == None:
        return jsonify("Error: Data must have a 'price' key")

    new_record = Food(title, price, menu_type)
    db.session.add(new_record)
    db.session.commit()

    return jsonify("Food item added successfully")

@app.route("/food/get", methods=["GET"])
def get_foods():
    records = db.session.query(Food).all()
    return jsonify(multiple_food_schema.dump(records))

@app.route("/food/get/<menu_type>", methods=['GET'])
def get_items_by_type(menu_type):
    records = db.session.query(Food).filter(Food.menu_type == menu_type).all()
    return jsonify(multiple_food_schema.dump(records))

if __name__ == "__main__":
    app.run(debug=True)