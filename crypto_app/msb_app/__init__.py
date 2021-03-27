# init.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from crypto_utils.signatures import SignerBlindSignature
from crypto_utils.conversions import SigConversion
from charm.toolbox.integergroup import IntegerGroupQ
from dateutil.relativedelta import *
from dateutil.easter import *
from datetime import date

# now = parse("Tues March 23 17:13:46 UTC 2020")
today = date.today()
rdelta = relativedelta(easter(2021), today)

# init SQLAlchemy so we can use it later in our models

db = SQLAlchemy()

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


def create_app():
    app = Flask(__name__, template_folder='templates')
    
    # initialise public key
    signer = SignerBlindSignature(IntegerGroupQ())
    app.config['signer'] = signer
    app.config['pubkey'] = SigConversion.convert_dict_strlist(signer.get_public_key())
    app.config['key_expiration'] = today + rdelta
    
    # database init info
    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['msb1'] = 'msb1:5000'
    app.config['msb2'] = 'msb2:5000'
    app.config['msb3'] = 'msb3:5000'
    app.config['msb4'] = 'msb4:5000'
    app.config['msb5'] = 'msb5:5000'

    db.init_app(app)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    db.create_all(app=app)
    return app