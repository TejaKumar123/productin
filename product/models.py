from product import db,app
from flask_login import UserMixin

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(30),unique=True,nullable=False)
    email=db.Column(db.String(50),unique=True,nullable=False)
    password=db.Column(db.String(50),nullable=False)
    isadmin=db.Column(db.Boolean,default=False)

    def __init__(self,u,e,p,isa):
        self.username=u
        self.email=e
        self.password=p
        self.isadmin=isa

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def __repr__(self):
        return f"username:{self.username}\nemail:{self.email}\npassword:{self.password}"


class product(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(30),nullable=False,unique=True)
    price=db.Column(db.Float,nullable=False)
    description=db.Column(db.String(200),nullable=False,unique=True)

    def __init__(self,n,p,d):
        self.name=n
        self.price=p
        self.description=d

    def __repr__(self):
        return f"product {self.id}"

class booking(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    cid=db.Column(db.Integer,unique=False,nullable=False)
    pid=db.Column(db.Integer,nullable=False,unique=False)
    def __init__(self,c,p):
        self.cid=c
        self.pid=p
    def __repr__(self):
        return f"{self.cid}:{self.pid}"
