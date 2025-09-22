#user_routes.py
from flask import Blueprint, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired, Length, Email

user_bp = Blueprint('user_bp', __name__)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

@user_bp.route('/')
def user_index():
    return render_template('user_index.html')

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    return render_template('register.html', form=form)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

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