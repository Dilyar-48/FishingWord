from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    email = StringField('Login(email)', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=50, message="Имя должно быть от 2 до 50 символов")])
    surname = StringField('Фамилия', validators=[DataRequired(), Length(min=2, max=50, message="Фамилия должна быть от 2 до 50 символов")])
    town = StringField('Город', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, message="Пароль должен быть не менее 6 символов")])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password', message="Пароли не совпадают")])
    submit = SubmitField('Зарегистрироваться')