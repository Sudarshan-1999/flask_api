from . import db
from sqlalchemy.sql import func
class Users(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable= False)
    password = db.Column(db.String(500), nullable= False)
    email = db.Column(db.String(200),unique=True, nullable=False)
    created_at= db.Column(db.DateTime(timezone=True),server_default=func.now())    
    funds = db.relationship("Funds", backref="Users")
    def __repr__(self):
        return f"<User {self.firstname} {self.id}"
    
class Funds(db.Model):
    __tablename__ = "Funds"
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10,2))
    userId = db.Column(db.Integer, db.ForeignKey("Users.id"))
    created_at= db.Column(db.DateTime(timezone=True),server_default=func.now())    

    @property
    def serialize(self):
        return {
            "id" : self.id,
            "amount": self.amount,
            "created_at": self.created_at
        }

