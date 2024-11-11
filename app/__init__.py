from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
# Initialize the database
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    # Configuration settings for the app
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Adjust URI as needed
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "your-secure-app-secret-key"  # Replace with a secure secret key
    # Initialize the extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    # Import models for migration
    with app.app_context():
        from app import models  # Ensure models are loaded
    from app.models import User  # Import the User model (adjust the path as needed)
    login_manager = LoginManager()
    login_manager.init_app(app)

# Configure login_view (this is the route where users are redirected if they're not logged in)
    login_manager.login_view = 'main_routes.signin'  # Adjust to your actual login route

# Define how Flask-Login loads a user from a user ID
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id)) 
    return app


