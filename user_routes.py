from database import db
from flask import render_template, redirect, Blueprint, url_for, session
from functools import wraps

user_bp = Blueprint('user_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if not session.get('user_id'):
            return redirect(url_for('user_bp.login'))
        return f(*args,**kwargs)
    return decorated_function


@user_bp.route('/')
@login_required
def index():
    return render_template('index.html', profiles=None)

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@user_bp.route('/show_users', methods=['GET'])
@login_required
def show_users():
    return render_template('index.html', profiles=None)

@user_bp.route('/user/<int:user_id>')
@login_required
def user_info(user_id):
    return render_template('user_info.html', user_id=user_id)

@user_bp.route('/add_data', methods=['GET', 'POST'])
@login_required
def add_data():
    return render_template('add_data.html')

@user_bp.route('/delete/<int:id>')
@login_required
def delete(id):
    return redirect(url_for('user_bp.index'))

@user_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('user_bp.login'))