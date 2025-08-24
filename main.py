import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
database_url = os.environ.get("DATABASE_URL")

# Configure PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Avoids warning

# Create SQLAlchemy instance
db = SQLAlchemy(app)

def main():
    pass

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    with app.app_context(): # Nedded for db operations
        db.create_all()     # Creates the database and tables
    app.run(debug=True)
