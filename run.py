# Application entry point
from app.main import app, db

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        print("Database initialized")
    
    # Run the application
    app.run(host='0.0.0.0', port=4444, debug=True)
