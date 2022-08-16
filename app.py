from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_bcrypt import Bcrypt

import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite")
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
CORS(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique = True, nullable = False) 
    password = db.Column(db.String(30), nullable = False)
    meal = db.relationship('Food', backref='user', cascade = 'all, delete, delete-orphan') #allows our user to have access to the food table

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_type=db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    user_fk = db.Column(db.Integer, db.ForeignKey('user.id')) #foreign key

    def __init__(self, title, price, menu_type, user_fk):
        self.title = title
        self.price = price
        self.menu_type = menu_type
        self.user_fk = user_fk


class FoodSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "price", "menu_type", "user_fk")

food_schema = FoodSchema()
multiple_food_schema = FoodSchema(many=True)

class UserSchema(ma.Schema): 
    class Meta:
        fields = ('id', 'username', 'password', 'meal')
    meal = ma.Nested(multiple_food_schema)

user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)

#Food End Points
@app.route("/food/add", methods=["POST"])
def add_food():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")
    
    post_data = request.get_json()
    title = post_data.get("title")
    price = post_data.get("price")
    menu_type = post_data.get("menu-type")
    user_fk = post_data.get("user_fk")
    

    if title == None:
        return jsonify("Error: Data must have a 'title' key")
    if price == None:
        return jsonify("Error: Data must have a 'price' key")

    new_record = Food(title, price, menu_type, user_fk)
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

#User End Points
@app.route('/user/add', methods = ['POST'])
def add_user():
    post_data = request.get_json()
    username = post_data.get('username')
    password = post_data.get('password')
    user = db.session.query(User).filter(User.username == username).first()

    if user is not None:
        return jsonify('Error: You must use another name. That one is taken')

    encrypted_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username, encrypted_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify('You have created a user! Welcome to our site!')

@app.route('/user/get/<id>', methods = ['GET'])
def get_user(id):
    user = db.session.query(User).filter(User.id == id).first()
    return jsonify(user_schema.dump(user))

if __name__ == "__main__":
    app.run(debug=True)