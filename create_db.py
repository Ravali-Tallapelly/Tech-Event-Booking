from app import create_app, db
from app.models import User

# Create a Flask app instance
app = create_app()

# Use the app context
with app.app_context():
    # Create the database and tables
    db.create_all()

    # Insert a new user (example)
    user = User(username='veda', email='veda@example.com', password_hash='hashedpassword', account_type='basic')
    db.session.add(user)
    db.session.commit()

    print("Database created and user added.")
