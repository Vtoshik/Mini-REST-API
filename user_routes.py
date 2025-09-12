#user_routes.py
from flask import render_template, redirect, Blueprint, url_for

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/')
def user_index():
    return render_template('user_index.html')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@user_bp.route('/add_note')
def add_note():
    return render_template('add_note.html')

@user_bp.route('/note/<int:note_id>')
def note_info(note_id):
    return render_template('note_info.html', note_id=note_id)

@user_bp.route('/delete/<int:id>')
def delete_note():
    return redirect(url_for('user_bp.user_index'))

@user_bp.route('/logout')
def user_logout():
    return redirect(url_for('user_bp.login'))