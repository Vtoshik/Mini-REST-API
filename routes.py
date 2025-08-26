from database import db
from models.user import User
from models.note import Note
from flask import render_template, request, redirect, Blueprint, url_for

user_bp = Blueprint('user_bp', __name__)

# function to render index page
@user_bp.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', profiles=users)

from flask import request, redirect, url_for

@user_bp.route('/add_data', methods=['GET', 'POST'])
def add_data():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_data.html')

@user_bp.route('/delete/<int:id>')
def delete(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('index'))