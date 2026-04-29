from flask import Flask, render_template, redirect, request, session
from data import db_session
from data.users import User
from form import LoginForm, RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def index():
    return render_template('index.html', title='Главная страница')


@app.route('/map')
def map():
    if not session.get('user_id'):
        return redirect('/login')
    return render_template('base.html', title='Карта')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect('/')

    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect('/')

        return render_template('login.html', title='Авторизация', form=form, message="Неправильный email или пароль")

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect('/')

    form = RegisterForm()
    if form.validate_on_submit():
        try:
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")

            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация', form=form,
                                       message="Такой пользователь уже есть")

            user = User(
                email=form.email.data,
                name=form.name.data,
                surname=form.surname.data,
                town=form.town.data
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()

            return render_template('login.html', title='Авторизация', form=LoginForm(), message="Регистрация успешна!")
        except Exception as e:
            return f"Ошибка: {e}"

    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1')