#admin_routes.py
from flask import render_template, redirect, Blueprint, url_for, abort
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/')
@jwt_required()
def admin_index():
    return render_template('admin_index.html', profiles=None)

@admin_bp.route('/show_users')
@jwt_required()
def show_users():
    return render_template('admin_index.html', profiles=None)

@admin_bp.route('/user/<int:user_id>')
@jwt_required()
def user_info(user_id):
    return render_template('user_info.html', user_id=user_id)

@admin_bp.route('/add_data')
@jwt_required()
def add_data():
    return render_template('add_data.html')

@admin_bp.route('/delete/<int:id>')
@jwt_required()
def delete():
    return redirect(url_for('admin_bp.admin_index'))