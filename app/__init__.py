import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    load_dotenv()
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-in-prod')

    db_url = os.getenv('DATABASE_URL', 'sqlite:///medi_share_dev.db')
    # SQLAlchemy requires postgresql+psycopg2:// — fix Neon/Heroku-style URLs
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    elif db_url.startswith('postgresql://'):
        db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    # psycopg2 does not support channel_binding — strip it from the URL
    db_url = db_url.replace('&channel_binding=require', '').replace('?channel_binding=require&', '?').replace('?channel_binding=require', '')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Reconnect automatically when Neon's pooler drops idle SSL connections
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    bcrypt.init_app(app)
    
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Blueprints
    from app.auth_routes import auth_bp
    from app.dashboard_routes import dash_bp
    from app.patient_routes import patient_bp
    from app.record_routes import record_bp
    from app.share_routes import share_bp
    from app.hospital_routes import hospital_bp
    from app.main_routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(record_bp)
    app.register_blueprint(share_bp)
    app.register_blueprint(hospital_bp)
    app.register_blueprint(main_bp)
    
    with app.app_context():
        db.create_all()
    
    return app

