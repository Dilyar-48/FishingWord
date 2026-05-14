import random

from flask import Flask, render_template, redirect, request, session, abort, jsonify
from data import db_session, trips_api
from data.users import User
from data.plans import Plan
from form import LoginForm, RegisterForm, PlanForm, ProfileForm
import os
from geopy.distance import distance
import folium
from geopy.geocoders import Nominatim
import requests
from requests import get, post, delete

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
URL = "https://discover.search.hereapi.com/v1/discover"

UPLOAD_FOLDER = 'static/avatars'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html', title='Главная страница')


@app.route('/help')
def help():
    return render_template('help.html', title='Помощь')


@app.route('/map/<dist>')
def map(dist):
    if not session.get('user_id'):
        return redirect('/login')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == session['user_id']).first()
    geolocator = Nominatim(user_agent="my_application")
    location = geolocator.geocode(user.town)
    if location is None:
        location = geolocator.geocode("Москва")
        user.town = "Москва"
    map = folium.Map(location=[location.latitude, location.longitude], width="100%", height="100%")
    folium.Marker(location=[location.latitude, location.longitude], popup=user.town,
                  icon=folium.Icon(color='red')).add_to(map)
    loc = (location.latitude, location.longitude)
    map.get_root().render()
    iframe = map._repr_html_()
    responce = requests.get(
        f"http://api.geonames.org/findNearbyJSON?lat={location.latitude}&lng={location.longitude}&lang=ru&radius={dist}&featureClass=H&maxRows=50&username=dilly38")
    try:
        for water in responce.json()["geonames"]:
            name = ""
            color = ""
            line_coordinates = [[location.latitude, location.longitude]]
            if "река" in water["fcodeName"].lower():
                name = f"р.{water['name']}"
                color = "blue"
            elif "озеро" in water["fcodeName"].lower():
                name = water['name']
                color = "green"
            elif "пруд" in water["fcodeName"].lower():
                name = f"п.{water['name']}"
                color = "green"
            if name != "":
                location2 = (float(water["lat"]), float(water["lng"]))
                line_coordinates.append([float(water["lat"]), float(water["lng"])])
                km = round(distance(loc, location2).km, 2)
                marker = folium.CircleMarker(location=[float(water["lat"]), float(water["lng"])],
                                             popup=f"{name}\nРасстояние по прямой: {km} км\n{location2[0]}, {location2[1]}",
                                             fill_color=color, color="white", fill_opacity=0.9)
                marker.add_to(map)

                line = folium.PolyLine(locations=line_coordinates, color=random.choice(["pink", "yellow", "orange"]),
                                       weight=5, opacity=0.8)
                line.add_to(map)

        map.get_root().render()
        iframe = map._repr_html_()
        return render_template('map.html', title='Карта', iframe=iframe)
    except Exception:
        return render_template('map.html', title='Карта', iframe=iframe)


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
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_surname'] = user.surname
            return redirect('/')
        except Exception as e:
            return f"Ошибка: {e}"

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/submit', methods=['POST'])
def submit():
    form_value = request.form.get('number')
    if form_value == "":
        return redirect(f'/map/20')
    return redirect(f'/map/{form_value}')


@app.route('/trips')
def trips():
    if not session.get('user_id'):
        return redirect('/login')
    user_plans = get('http://localhost:8080/api/trips').json()["trips"]
    return render_template('trips.html', title='Мои поездки', plans=user_plans, user=session.get('user_id'))


@app.route('/create_plan', methods=['GET', 'POST'])
def create_plan():
    if not session.get('user_id'):
        return redirect('/login')
    form = PlanForm()
    if form.validate_on_submit():
        post('http://localhost:8080/api/trips', json={'place': form.place.data, 'count_people': form.count_people.data, 'data': form.data.data.strftime("%d-%m-%Y"), 'time': form.time.data.strftime("%H-%M"), 'leader_id': session['user_id']})
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
    delete(f'http://localhost:8080/api/trips/{id}').json()
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
    app.register_blueprint(trips_api.blueprint)
    app.run(port=8080, host='0.0.0.0', debug=True)
