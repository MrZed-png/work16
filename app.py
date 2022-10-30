import json

import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import raw_data

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(50))

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "email": self.email,
            "role": self.role,
            "phone": self.phone,
        }


class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    start_date = db.Column(db.String(100))
    end_date = db.Column(db.String(100))
    address = db.Column(db.String(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey(f"{User.__tablename__}.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey(f"{User.__tablename__}.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "address": self.address,
            "price": self.price,
            "customer_id": self.customer_id,
            "executor_id": self.executor_id,
        }


class Offer(db.Model):
    __tablename__ = "offer"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey(f"{Order.__tablename__}.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey(f"{User.__tablename__}.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "executor_id": self.executor_id,
        }


@app.route("/users", methods=["GET", "POST"])
def users():
    if requests.method == "GET":
        result = []
        for u in User.query.all():
            result.append(u.to_dict())

        return json.dumps(result), 200, {'Content-Type': 'application/json'}

    if requests.method == "POST":
        user_data = json.loads(requests.data)

        new_user = User(
            id=user_data.get("id"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            age=user_data.get("age"),
            email=user_data.get("email"),
            role=user_data.get("role"),
            phone=user_data.get("phone"),
        )
        db.session.add(new_user)
        db.session.commit()

        return "", 201


@app.route("/users/<int:uid>", methods=["GET"])
def user(uid: int):
    return json.dumps(User.query.get(uid).to_dict()), 200, {'Content-Type': 'application/json'}


@app.route("/orders", methods=["GET"])
def orders():
    result = []
    for u in Order.query.all():
        result.append(u.to_dict())

    return json.dumps(result), 200, {'Content-Type': 'application/json'}


@app.route("/orders/<int:uid>", methods=["GET"])
def order(uid: int):
    return json.dumps(Order.query.get(uid).to_dict()), 200, {'Content-Type': 'application/json'}


@app.route("/offers", methods=["GET"])
def offers():
    result = []
    for u in Offer.query.all():
        result.append(u.to_dict())

    return json.dumps(result), 200, {'Content-Type': 'application/json'}


@app.route("/offers/<int:uid>", methods=["GET"])
def offer(uid: int):
    return json.dumps(Offer.query.get(uid).to_dict()), 200, {'Content-Type': 'application/json'}


def init_database():
    db.drop_all()
    db.create_all()

    for user_data in raw_data.users:
        new_user = User(
            id=user_data.get("id"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            age=user_data.get("age"),
            email=user_data.get("email"),
            role=user_data.get("role"),
            phone=user_data.get("phone"),
        )
        db.session.add(new_user)
        db.session.commit()

    for order_data in raw_data.orders:
        new_order = Order(
            id=order_data.get("id"),
            name=order_data.get("name"),
            description=order_data.get("description"),
            start_date=order_data.get("start_date"),
            end_date=order_data.get("end_date"),
            address=order_data.get("address"),
            price=order_data.get("price"),
            customer_id=order_data.get("customer_id"),
            executor_id=order_data.get("executor_id"),
        )
        db.session.add(new_order)
        db.session.commit()

    for offer_data in raw_data.offers:
        new_offer = Offer(
            id=offer_data.get("id"),
            order_id=offer_data.get("order_id"),
            executor_id=offer_data.get("executor_id"),
        )
        db.session.add(new_offer)
        db.session.commit()


if __name__ == '__main__':
    init_database()
    app.run(debug=True)
