from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
import psycopg2

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap(app)
mail = Mail(app)

from app import routes, models








#In Python, a sub-directory that includes a __init__.py file is considered a
#package, and can be imported. When you import a package, the __init__.py
#executes and defines what symbols the package exposes to the outside world.
