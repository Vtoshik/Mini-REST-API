#admin_routes.py
from flask import render_template, redirect, Blueprint, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Add User')

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/')
def admin_index():
    return render_template('admin_index.html', profiles=None)

@admin_bp.route('/show_users')
def show_users():
    return render_template('admin_index.html', profiles=None)

@admin_bp.route('/user/<int:user_id>')
def user_info(user_id):
    form = AddUserForm()
    return render_template('user_info.html', form=form, user_id=user_id)

@admin_bp.route('/add_data')
def add_data():
    form = AddUserForm()
    return render_template('add_data.html', form=form)

@admin_bp.route('/delete/<int:id>')
def delete():
    return redirect(url_for('admin_bp.admin_index'))