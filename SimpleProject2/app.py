from flask import Flask, render_template, request, redirect, url_for, flash, make_response
import os
import json


# JSONDB klases definīcija
class JSONDB:
    def __init__(self, filename):
        self.filename = filename
        self.load_data()

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
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

    def get_reviews_for_restaurant(self, restaurant_id):
        return [r for r in self.data['reviews'] if r['restaurant_id'] == restaurant_id]

    def add_review(self, user_id, restaurant_id, rating, comment):
        new_id = max((r['id'] for r in self.data['reviews']), default=0) + 1
        new_review = {
            'id': new_id,
            'user_id': user_id,
            'restaurant_id': restaurant_id,
            'rating': rating,
            'comment': comment
        }
        self.data['reviews'].append(new_review)
        self.save_data()

    def add_user(self, user):
        self.data['users'].append(user)
        self.save_data()

    def add_image(self, image):
        self.data['images'].append(image)
        self.save_data()
        
# JSONDB klases gadījuma izveide
db = JSONDB('data.json')


app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Datu struktūra restorānu un atsauksmju glabāšanai
restaurants = []
reviews = {}


DATA_FILE = 'data.json'


# Notiek datu ielāde
def load_data():
    global restaurants, reviews
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            restaurants = data.get('restaurants', [])
            reviews = data.get('reviews', {})


# Datu saglabāšana
def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'restaurants': restaurants, 'reviews': reviews}, f, ensure_ascii=False, indent=4)


load_data()


# Pievienojiet jaunu restorāna lapu
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


# Lapa, lai parādītu visus restorānus
@app.route('/')
def index():
    restaurants = db.get_restaurants()
    return render_template('index.html', restaurants=restaurants)


# Lapa atsauksmes pievienošanai
@app.route('/add_review/<restaurant_name>', methods=['GET','POST'])
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

@app.route('/restaurant/<restaurant_name>')
def view_restaurant(restaurant_name):
    restaurants = db.get_restaurants()
    restaurant = next((r for r in restaurants if r['name'] == restaurant_name), None)
    if restaurant is None:
        return "Restaurant not found", 404

    all_reviews = db.get_reviews()
    restaurant_reviews = [r for r in all_reviews if r['restaurant_id'] == restaurant['id']]

    resp = make_response(render_template('restaurant.html', restaurant=restaurant, reviews=restaurant_reviews))
    resp.set_cookie('last_visited', restaurant_name)
    return resp

# Lapa viena restorāna un tā atsauksmju apskatei
# @app.route('/restaurant/<restaurant_name>')
# def view_restaurant(restaurant_name):
#     # Atrodiet restorānu pēc nosaukuma
#     restaurant = next((r for r in restaurants if r['name'] == restaurant_name), None)
#     restaurant_reviews = reviews.get(restaurant_name, [])


#     # Ja restorāns netiek atrasts, atgrieziet kļūdu vai novirziet
#     if restaurant is None:
#         return "Restorāns nav atrasts", 404
#     all_reviews = db.get_reviews()
#     restaurant_reviews = [r for r in all_reviews if r['restaurant_id'] == restaurant['id']]

#     resp = make_response(render_template('restaurant.html', restaurant=restaurant, reviews=restaurant_reviews))
#     resp.set_cookie('last_visited', restaurant_name)
#     return resp

    # Mēs saglabājam informāciju par pēdējo apmeklēto restorānu sīkfailā
    # resp = make_response(render_template('restaurant.html', restaurant=restaurant, reviews=restaurant_reviews))
    # resp.set_cookie('last_visited', restaurant_name)  # Pēdējā apmeklētā restorāna nosaukumu saglabājam sīkdatnē
    # return resp


# Lapa informācijas attēlošanai par restorānu un tā atsauksmēm
# @app.route('/restaurant/<restaurant_name>')
# def view_restaurant(restaurant_name):
#     restaurant = next((r for r in db.get_restaurants() if r['name'] == restaurant_name), None)
#     restaurant_reviews = db.get_reviews().get(restaurant_name, [])
#     return render_template('restaurant.html', restaurant=restaurant, reviews=restaurant_reviews)


# Visas atsauksmes
@app.route('/all_reviews')
def all_reviews():
    all_data = []
    for name, revs in reviews.items():
        for rev in revs:
            all_data.append({'restaurant': name, 'rating': rev['rating'], 'comment': rev['comment']})
    return render_template('all_reviews.html', reviews=all_data)


if __name__ == '__main__':
    app.run(debug=True)
