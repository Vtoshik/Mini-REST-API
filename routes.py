from database import db
from models.user import User
from models.note import Note
from flask import render_template, request, redirect, Blueprint, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

user_bp = Blueprint('user_bp', __name__)
    
def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if not session.get('user_id'):
            return redirect(url_for('user_bp.login'))
        return f(*args,**kwargs)
    return decorated_function

# function to render index page
@user_bp.route('/')
@login_required
def index():
    user_id = session.get('user_id')
    if user_id:
        return render_template('index.html', profiles=None)
    else:
        return redirect(url_for('user_bp.login'))

@user_bp.route('/show_users', methods=['GET'])
@login_required
def show_users():
    profiles = User.query.all()
    return render_template('index.html', profiles=profiles)

from flask import request, redirect, url_for

@user_bp.route('/add_data', methods=['GET', 'POST'])
@login_required
def add_data():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_bp.index'))
    return render_template('add_data.html')

@user_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user_bp.index'))

@user_bp.route('/user/<int:user_id>')
@login_required
def user_info(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_info.html', user=user)

@user_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('user_bp.index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@user_bp.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        existing_user = User.query.filter(
            (User.email == email) | (User.username == username)
        ).first()
        if existing_user:
            return render_template('register.html', error="User with this email or username already exists.")

        user = User(username = username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_bp.login'))
    return render_template('register.html')

@user_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('user_bp.login'))