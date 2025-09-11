#admin_routes.py
from flask import render_template, redirect, Blueprint, url_for, abort
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

admin_bp = Blueprint('admin_bp', __name__)

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.status != 'admin':
            abort(403, description="Admin access required")
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
#@admin_required
def admin_index():
    return render_template('admin_index.html', profiles=None)

@admin_bp.route('/show_users')
#@admin_required
def show_users():
    return render_template('admin_index.html', profiles=None)

@admin_bp.route('/user/<int:user_id>')
#@admin_required
def user_info(user_id):
    return render_template('user_info.html', user_id=user_id)

@admin_bp.route('/add_data')
#@admin_required
def add_data():
    return render_template('add_data.html')

@admin_bp.route('/delete/<int:id>')
#@admin_required
def delete():
    return redirect(url_for('admin_bp.admin_index'))