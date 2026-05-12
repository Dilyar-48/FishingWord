from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, IntegerField, DateField, TimeField
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    email = EmailField('Login(email)', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Login(email)', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=50, message="Имя должно быть от 2 до 50 символов")])
    surname = StringField('Фамилия', validators=[DataRequired(), Length(min=2, max=50, message="Фамилия должна быть от 2 до 50 символов")])
    town = StringField('Город', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, message="Пароль должен быть не менее 6 символов")])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password', message="Пароли не совпадают")])
    submit = SubmitField('Зарегистрироваться')


class PlanForm(FlaskForm):
    place = StringField('Место рыбалки', validators=[DataRequired()])
    count_people = IntegerField('Нужно человек', validators=[DataRequired()])
    data = DateField('Дата', validators=[DataRequired()])
    time = TimeField('Время', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class ProfileForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    town = StringField('Город', validators=[DataRequired()])
    avatar = FileField('Аватарка', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Только картинки!')])
    submit = SubmitField('Сохранить')