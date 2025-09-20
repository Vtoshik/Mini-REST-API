#admin_routes.py
from flask import render_template, redirect, Blueprint, url_for

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/')
def admin_index():
    return render_template('admin_index.html', profiles=None)

@admin_bp.route('/show_users')
def show_users():
    return render_template('admin_index.html', profiles=None)

@admin_bp.route('/user/<int:user_id>')
def user_info(user_id):
    return render_template('user_info.html', user_id=user_id)

@admin_bp.route('/add_data')
def add_data():
    return render_template('add_data.html')

@admin_bp.route('/delete/<int:id>')
def delete():
    return redirect(url_for('admin_bp.admin_index'))