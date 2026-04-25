from flask import Flask, render_template, url_for
from form import LoginForm, RegisterForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def index():
    return render_template('index.html', title='Главная страница')


@app.route('/map')
def map():
    return render_template('base.html', title='Карта')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    return render_template('register.html', title='Регистрация', form=form)

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')