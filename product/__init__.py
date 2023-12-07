from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_login import LoginManager
import os

app=Flask(__name__)

current_directory = os.path.abspath(os.path.dirname(__file__))
relative_path = 'example.db'
database_path = os.path.join(current_directory, relative_path)

app.config["SQLALCHEMY_DATABASE_URI"]=f"sqlite:///{database_path}"
app.config["SECRET_KEY"]="0a0d4557e3b2869b2733897ff79dd0d2"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days = 1)

db=SQLAlchemy(app)

login_manager=LoginManager(app)
login_manager.login_view="signin"


from product import routes
