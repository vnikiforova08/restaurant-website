from flask import Flask, render_template, request, redirect, url_for, flash, make_response
import os
import json


# Определение класса JSONDB
class JSONDB:
    def __init__(self, filename):
        self.filename = filename
        self.load_data()


    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            # Если файла нет, создаем структуру с пустыми данными
            self.data = {
                "users": [],
                "restaurants": [],
                "reviews": [],
                "images": []
            }


    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)


    def get_restaurants(self):
        return self.data['restaurants']


    def get_reviews(self):
        return self.data['reviews']


    def add_restaurant(self, restaurant):
        self.data['restaurants'].append(restaurant)


    def add_review(self, review):
        self.data['reviews'].append(review)


    def add_user(self, user):
        self.data['users'].append(user)


    def add_image(self, image):
        self.data['images'].append(image)
# Создание экземпляра класса JSONDB
db = JSONDB('data.json')


app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Структура данных для хранения ресторанов и отзывов
restaurants = []
reviews = {}


DATA_FILE = 'data.json'


# Загрузка данных
def load_data():
    global restaurants, reviews
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            restaurants = data.get('restaurants', [])
            reviews = data.get('reviews', {})


# Сохранение данных
def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'restaurants': restaurants, 'reviews': reviews}, f, ensure_ascii=False, indent=4)


load_data()


# Страница добавления нового ресторана
@app.route('/add_restaurant', methods=['GET', 'POST'])
def add_restaurant():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        description = request.form['description']


        if not name or not address:
            flash('Lūdzu, aizpildiet visus laukus.')
            return redirect(url_for('add_restaurant'))


        db.add_restaurant({'name': name, 'address': address, 'description': description})
        db.save_data()
        flash(f'Restorāns {name} ir pievienots!')
        return redirect(url_for('index'))


    return render_template('add_restaurant.html')


# Страница для отображения всех ресторанов
@app.route('/')
def index():
    restaurants = db.get_restaurants()
    return render_template('index.html', restaurants=restaurants)


# Страница для добавления отзыва
@app.route('/add_review/<restaurant_name>', methods=['GET', 'POST'])
def add_review(restaurant_name):
    if request.method == 'POST':
        rating = request.form['rating']
        comment = request.form['comment']


        if not comment or not rating:
            flash('Lūdzu, aizpildiet abus laukus.')
            return redirect(url_for('add_review', restaurant_name=restaurant_name))


        db.add_review(restaurant_name, {'rating': rating, 'comment': comment})
        db.save_data()
        flash(f'Atsauksme par {restaurant_name} ir pievienota!')
        return redirect(url_for('view_restaurant', restaurant_name=restaurant_name))


    return render_template('add_review.html', restaurant_name=restaurant_name)


# Страница для просмотра одного ресторана и его отзывов
@app.route('/restaurant/<restaurant_name>')
def view_restaurant(restaurant_name):
    # Находим ресторан по имени
    restaurant = next((r for r in restaurants if r['name'] == restaurant_name), None)
    restaurant_reviews = reviews.get(restaurant_name, [])


    # Если ресторан не найден, возвращаем ошибку или перенаправляем
    if restaurant is None:
        return "Ресторан не найден", 404


    # Сохраняем информацию о последнем посещенном ресторане в cookie
    resp = make_response(render_template('restaurant.html', restaurant=restaurant, reviews=restaurant_reviews))
    resp.set_cookie('last_visited', restaurant_name)  # Сохраняем в cookie имя последнего посещенного ресторана
    return resp


# Страница для отображения информации о ресторане и его отзывах
@app.route('/restaurant/<restaurant_name>')
def view_restaurant(restaurant_name):
    restaurant = next((r for r in db.get_restaurants() if r['name'] == restaurant_name), None)
    restaurant_reviews = db.get_reviews().get(restaurant_name, [])
    return render_template('restaurant.html', restaurant=restaurant, reviews=restaurant_reviews)


# Все отзывы
@app.route('/all_reviews')
def all_reviews():
    all_data = []
    for name, revs in reviews.items():
        for rev in revs:
            all_data.append({'restaurant': name, 'rating': rev['rating'], 'comment': rev['comment']})
    return render_template('all_reviews.html', reviews=all_data)


if __name__ == '__main__':
    app.run(debug=True)
