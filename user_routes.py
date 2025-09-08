from database import db
from flask import render_template, redirect, Blueprint, url_for, session
from functools import wraps

user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/')
def index():
    return render_template('index.html', profiles=None)

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@user_bp.route('/show_users', methods=['GET'])
def show_users():
    return render_template('index.html', profiles=None)

@user_bp.route('/user/<int:user_id>')
def user_info(user_id):
    return render_template('user_info.html', user_id=user_id)

@user_bp.route('/add_data', methods=['GET', 'POST'])
def add_data():
    return render_template('add_data.html')

@user_bp.route('/delete/<int:id>')
def delete():
    return redirect(url_for('user_bp.index'))

@user_bp.route('/add_note')
def add_note():
    return render_template('add_note.html')

@user_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('user_bp.login'))