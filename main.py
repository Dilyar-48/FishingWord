from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title='Главная страница')


@app.route('/map')
def map():
    return render_template('base.html', title='Карта')

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')