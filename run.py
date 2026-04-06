"""
Main application entry point
"""
from app import create_app
import os

os.environ['FLASK_ENV'] = 'production'

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4444, debug=False)
