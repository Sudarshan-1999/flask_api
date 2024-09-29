from functools import wraps
from . import app, db
from flask import request, make_response
from .models import Users, Funds
import jwt
from datetime import datetime, timedelta
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
@app.route('/signup', methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    password = data.get("password")
    if firstname and lastname and email and password:
        user = Users.query.filter_by(email=email).first()
        if user:
            return make_response({
                "message": "Please Sign In"
            }, 200)
        user = Users(
            email = email,
            password= generate_password_hash(password),
            firstname= firstname,
            lastname = lastname
        )
        print(user)
        db.session.add(user)
        db.session.commit()
        return make_response({
            "message": "User Created"
        }, 201)
    return make_response({
        "message": "Unable to create user"
    }, 500)

@app.route("/login", methods=["GET"])
def login():
    auth = request.json
    if not auth or not auth.get('email') or not auth.get('password'):
        return make_response(
            {"message": "creadentials incorrects"},
            401
        )
    user = Users.query.filter_by(email =auth.get('email')).first()
    if not user:
        return make_response(
            {
                "message": "Please create account"
            },
            401
        )
    if check_password_hash(user.password, auth.get('password')):
        expiry_time = datetime.utcnow() + timedelta(minutes=10)
        token = jwt.encode({
            'id': user.id,
            'expiry': expiry_time.strftime('%Y-%m-%d %H:%M:%S')
        },
        "secret",
        "HS256"
        )
        return make_response({
            "token": token,
            'expiry': expiry_time.strftime('%Y-%m-%d %H:%M:%S')
        }, 201)
    return make_response({
        "message": "Please check your credentials"
    }, 401) 


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # f()
        token= None
        if 'Authorization' in request.headers:
            token = request.headers["Authorization"]
            # current_user = Users.query.filter_by(id=['id']).first()
            # print(current_user)
        if not token:
            return make_response({
            },401)
        try:
            data = jwt.decode(token, "secret", algorithms=["HS256"])
            current_user = Users.query.filter_by(id=data['id']).first()
            print(current_user)
        except Exception as err:
            print(err)
            return make_response({"message": "Token is invalid"}, 401)
        return f(current_user, *args, **kwargs)
    return wrapper

@app.route("/funds", methods=["GET"])
@token_required
def get_funds(current_user):
    funds=Funds.query.filter_by(userId=current_user.id).all()
    total_sum = 0
    if funds:
        total_sum = Funds.query.with_entities(db.func.round(func.sum(Funds.amount),2)).filter_by(userId=current_user.id).all()[0][0]
    return make_response({
        "data": [row.serialize for row in funds],
        "total": total_sum
    },200)

@app.route("/funds", methods=["POST"])
@token_required
def createFund(current_user):
    data = request.json
    print(data)
    amount = data.get('amount')
    if amount:
        fund = Funds(
            amount = amount,
            userId = current_user.id
        )
    db.session.add(fund)
    db.session.commit()
    return fund.serialize

@app.route("/funds/<id>", methods=["GET"])
@token_required
def getFundId(current_user,id):
    try:
        fund = Funds.query.filter_by(userId=current_user.id, id= id).first()
        if not fund:
            return make_response({"message" : "Unable to get fund"},401)
        return make_response({"message" : fund.serialize},200)
    except Exception as err:
        print(err)
        return make_response({"message" : "unable to proccess"},409)
    

@app.route("/funds/<id>", methods=["PUT"])
@token_required
def updateFund(current_user,id):
    try:
        fund = Funds.query.filter_by(userId=current_user.id, id= id).first()
        if not fund:
            return make_response({"message" : "Unable to update fund"},401)
        data = request.json
        amount= data.get('amount')
        if amount:
            fund.amount= amount
        db.session.commit()
        return make_response({"message" : fund.serialize},201)
    except Exception as err:
        print(err)
        return make_response({"message" : "unable to proccess"},409)
    
@app.route("/funds/<id>", methods=["DELETE"])
@token_required
def deleteFund(current_user,id):
    try:
        fund = Funds.query.filter_by(userId= current_user.id, id=id).first()
        if not fund:
            return make_response({"message": f"Fund not {id} found"},404)
        db.session.delete(fund)
        db.session.commit()
        return make_response({"message": fund.serialize},204)
    except Exception as err:
        print(err)
        return make_response({"message": "unable to proccess cause Error"},409)