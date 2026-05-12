from flask import Flask, render_template, redirect, request, session, abort
from data import db_session
from data.users import User
from data.plans import Plan
from form import LoginForm, RegisterForm, PlanForm, ProfileForm
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

UPLOAD_FOLDER = 'static/avatars'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
            session['user_surname'] = user.surname
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

            return redirect('/')
        except Exception as e:
            return f"Ошибка: {e}"

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/trips')
def trips():
    if not session.get('user_id'):
        return redirect('/login')
    db_sess = db_session.create_session()
    user_plans = db_sess.query(Plan).filter(Plan.leader_id == session['user_id']).all()
    return render_template('trips.html', title='Мои поездки', plans=user_plans)


@app.route('/create_plan', methods=['GET', 'POST'])
def create_plan():
    if not session.get('user_id'):
        return redirect('/login')
    form = PlanForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        plan = Plan()
        plan.place = form.place.data
        plan.count_people = form.count_people.data
        plan.users_count_now = 1
        plan.data = form.data.data
        plan.time = form.time.data
        plan.leader_id = session['user_id']
        db_sess.add(plan)
        db_sess.commit()
        return redirect('/trips')
    return render_template('plan.html', title='Создание поездки', form=form)


@app.route('/edit_plan/<int:id>', methods=['GET', 'POST'])
def edit_plan(id):
    if not session.get('user_id'):
        return redirect('/login')
    form = PlanForm()
    db_sess = db_session.create_session()
    plan = db_sess.query(Plan).filter(Plan.id == id, Plan.leader_id == session['user_id']).first()
    if not plan:
        abort(404)
    if request.method == "GET":
        form.place.data = plan.place
        form.count_people.data = plan.count_people
        form.data.data = plan.data
        form.time.data = plan.time
    if form.validate_on_submit():
        plan.place = form.place.data
        plan.count_people = form.count_people.data
        plan.data = form.data.data
        plan.time = form.time.data
        db_sess.commit()
        return redirect('/trips')
    return render_template('plan.html', title='Редактирование поездки', form=form)


@app.route('/delete_plan/<int:id>')
def delete_plan(id):
    if not session.get('user_id'):
        return redirect('/login')
    db_sess = db_session.create_session()
    plan = db_sess.query(Plan).filter(Plan.id == id, Plan.leader_id == session['user_id']).first()
    if plan:
        db_sess.delete(plan)
        db_sess.commit()
    return redirect('/trips')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == session['user_id']).first()

    form = ProfileForm()

    if form.validate_on_submit():
        user.name = form.name.data
        user.surname = form.surname.data
        user.town = form.town.data

        if form.avatar.data:
            file = form.avatar.data
            file.save(os.path.join('static/avatars', f"{session['user_id']}_{file.filename}"))
            user.avatar = f"{session['user_id']}_{file.filename}"

        db_sess.commit()
        session['user_name'] = user.name
        return redirect('/profile')

    elif request.method == 'GET':
        form.name.data = user.name
        form.surname.data = user.surname
        form.town.data = user.town

    return render_template('profile.html', title='Профиль', form=form, user=user)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1', debug=True)