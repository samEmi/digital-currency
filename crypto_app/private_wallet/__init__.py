# init.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, template_folder='templates')

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///private_wallet.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['msb1'] = '127.0.0.1:6000'
    app.config['msb2'] = '127.0.0.1:7000'
    app.config['msb3'] = 'msb3:5000'
    app.config['msb4'] = 'msb4:5000'
    app.config['msb5'] = 'msb5:5000'


    app.config['pos1'] = '127.0.0.1:7000'
    #TODO: need to configure params properly
    app.config['username'] = "123"
    app.config['password'] = "123"
    
    db.init_app(app)
    jwt.init_app(app)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    db.create_all(app=app)
    return app