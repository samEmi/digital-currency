# init.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from crypto_utils.signatures import SignerBlindSignature
from crypto_utils.conversions import SigConversion
from charm.toolbox.integergroup import IntegerGroupQ
import datetime
# from flask_login import LoginManager
from dateutil.relativedelta import *
from dateutil.easter import *
from datetime import date
from flask_jwt_extended import JWTManager
from charm.toolbox.ecgroup import ECGroup,ZR,G
from charm.toolbox.eccurve import prime192v1

 
today = datetime.datetime.now()
# rdelta = relativedelta(easter(2021), today)
rdelta = datetime.timedelta(hours=500)

# init SQLAlchemy so we can use it later in our models

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, template_folder='templates')
    
    # 1. key setup for blind signature
    signer = SignerBlindSignature(IntegerGroupQ())
    app.config['signer'] = signer
    app.config['pubkey'] = SigConversion.convert_dict_strlist(signer.get_public_key())
    app.config['key_expiration'] = today + rdelta

    # # 2. key setup for blind ring signature
    # group = ECGroup(prime192v1)
    # # get the ECC point from the ledger or hardcode it
    # # P has to be public info, known by all members of the ring and the user
    # P = keydb.get('P')
    # ring_pks = list()
    # for i in range(ring_size):
    #     ring_pks.append(keydb.FindKey(str(i)))
    # app.config['signer'] = SignerBlindRing(prime192v1, P, ring_pks=ring_pks)
 
    # database init info
    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///msb_app.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['msb1'] = 'msb1:5000'
    app.config['msb2'] = 'msb2:5000'
    app.config['msb3'] = 'msb3:5000'
    app.config['msb4'] = 'msb4:5000'
    app.config['msb5'] = 'msb5:5000'

    # login_manager = LoginManager()
    # login_manager.login_view = 'auth.login'
    # login_manager.init_app(app)

    # from cp.models.UserModel import UserModel

    # @login_manager.user_loader
    # def load_user(user_id):
    #     # since the user_id is just the primary key of our user table, use it in the query for the user
    #     return UserModel.query.get(int(user_id))

    # @jwt.user_loader_callback_loader
    # def user_loader_callback(identity):
    #     return UserModel.query.get(identity)

    db.init_app(app)
    jwt.init_app(app)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    db.create_all(app=app)
    return app