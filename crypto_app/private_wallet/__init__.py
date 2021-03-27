# init.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates')

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///private_wallet.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['msb1'] = 'msb1:5000'
    app.config['msb2'] = 'msb2:5000'
    app.config['msb3'] = 'msb3:5000'
    app.config['msb4'] = 'msb4:5000'
    app.config['msb5'] = 'msb5:5000'
    
    db.init_app(app)

    from private_wallet.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from private_wallet.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    db.create_all(app=app)
    return app