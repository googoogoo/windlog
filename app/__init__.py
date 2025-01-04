from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#The LoginManager class from the Flask-Login extension is used to manage the user authentication system.
from flask_login import LoginManager

#The app variable is an instance of Flask, and is the web application itself.
#The __name__ variable passed to the Flask class is a Python variable that is set to the name of the module in which it is used. 
#Flask uses the location of the module passed here as a starting point when it needs to load associated resources such as template files.
app = Flask(__name__)
#We apply the configuration settings defined in the Config class to the app
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

#From the app package, we import the routes module. The app package is defined by the app directory and the __init__.py script, and it contains the views and other logic.
from app import routes, models