from app import create_app
from app.routes import routes  # Ensure you import your blueprint here
# Create the Flask app
app = create_app()
app.register_blueprint(routes, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)
