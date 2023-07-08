import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient

import uuid
import requests
from dataclasses import asdict
from passlib.hash import pbkdf2_sha256
from flask import (
    flash,
    redirect,
    render_template,
    session,
    url_for,
    request
)

from api.models import Product, User
from api.forms import LoginForm, RegisterForm
from api.utils import login_required, update_amount

load_dotenv()

app = Flask(__name__)
app.config["MONGODB_URI"] = os.environ.get("MONGODB_URI")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.db = MongoClient(app.config["MONGODB_URI"]).get_default_database()



@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html", title="PetPalz - Home")


@app.route("/register", methods=["POST", "GET"])
def register():
    if session.get("email"):
        return redirect(url_for("home"))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            _id=uuid.uuid4().hex, 
            username=form.username.data,
            email=form.email.data, 
            password=pbkdf2_sha256.hash(form.password.data), 
        )                                                     

        app.db.user.insert_one(asdict(user))

        flash("User registered successfully", "success")
        return redirect(url_for("login"))

    return render_template(
        "register.html", title="Pet Palz - Register", form=form
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for("home"))

    form = LoginForm()
    if request.args.get('d') == 'demo':
        user_data = app.db.user.find_one({"email": "test@example.com"})
        user = User(**user_data)
        session["user_id"] = user._id
        session["email"] = user.email
        session["username"] = user.username
        session["address"] = None

        return redirect(url_for("login"))
    if form.validate_on_submit():
        
        user_data = app.db.user.find_one({"email": form.email.data})

        if not user_data:
            flash("Login credentials not correct", category="danger")
            return redirect(url_for("login"))

        user = User(**user_data)
        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            session["user_id"] = user._id
            session["email"] = user.email
            session["username"] = user.username
            session["address"] = None

            return redirect(url_for("home"))

        flash("Login credentials not correct", category="danger")
        
    return render_template("login.html", title="Pet Palz - Login", form=form)


@app.route("/logout")
@login_required
def logout():
    del session["username"]
    del session["email"]
    del session["user_id"]
    del session["csrf_token"]
    del session["address"]

    return redirect(url_for("home"))


@app.route("/product", methods=["GET", "POST"])
def product():
    product = Product(
        **(app.db.products.find_one({'title': request.args.get('p')}))
        )
    
    category = product.filters[0]  
    subcategory = product.filters[1]  

    if request.method == "POST":
        if not session:
            return redirect(url_for('login'))
        
        update_amount(product._id)

        return redirect(url_for('cart'))
    
    if not product.rating:
        rates_count = 0
        average_rating = 0
    else:
        rates_count = len(product.rating.values())
        average_rating = sum(product.rating.values())/rates_count

    return render_template(
        "product.html",
         title="PetPalz - Product",
         product=product,
         category=category,
         subcategory=subcategory,
         average_rating=average_rating,
         rates_count=rates_count
         )


@app.route("/cart/", methods=["GET", "POST"])
@login_required
def cart():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        update_amount(product_id)

        return redirect(url_for('cart'))
    
    user = User(**(app.db.user.find_one({'_id': session["user_id"] })))
    products_ids = [str(product_id) for product_id in user.cart.keys()]
    products_data = app.db.products.find({'_id': {'$in': products_ids} })
    products = [Product(**product) for product in products_data]

    total = sum([product.prices[0] * user.cart[product._id] for product in products])

    return render_template("cart.html", title="PetPalz - Cart", products=products, user=user, total=total, count=len(products))


categories = {'price': ['Up to $25', '$25 to $50', '$50 to $100', 'More than $100'],
              'brand': ['Purina', 'Iams', 'On-Airstore', 'AIMICOCA', 'Catit'] + ['Royal Canin', 'Primens', 'YROVWENQ', 'CuteBone'],
              'breed': ['Large Breeds', 'Medium Breeds', 'Small Breeds'],
              'stage': ['Adult', 'Puppy', 'Senior']}

@app.route('/<category>', methods=['GET', 'POST'])
@app.route('/<category>/<subcategory>', methods=['GET', 'POST'])
def pets(category, subcategory=None):
    sort_by = None
    selected_categories = []

    if subcategory:
        products_data = app.db.products.find({'filters': {'$all': [category, subcategory]}})
    else:
        products_data = app.db.products.find({'filters': {'$all': [category]}})

    if request.method == 'POST':
        selected_prices = [category]
        selected_brands = [category]
        selected_breeds = [category]
        selected_stages = [category]

        sort_by = request.form.get('sortOrder')

        if 'category-price' in request.form:
            selected_prices = request.form.getlist('category-price')
        if 'category-brand' in request.form:
            selected_brands = request.form.getlist('category-brand')
        if 'category-breed' in request.form:
            selected_breeds = request.form.getlist('category-breed')
        if 'category-stage' in request.form:
            selected_stages = request.form.getlist('category-stage')
        selected_categories = selected_prices + selected_brands + selected_breeds + selected_stages + [category]

        if subcategory:
            selected_categories += [subcategory]
            products_data = app.db.products.find({
                '$and': [
                {'filters': {'$in': selected_prices}},
                {'filters': {'$in': selected_brands}},
                {'filters': {'$in': selected_breeds}},
                {'filters': {'$in': selected_stages}},
                {'filters': {'$all': [category, subcategory]}}]})
        else:
            products_data = app.db.products.find({
                '$and': [
                {'filters': {'$in': selected_prices}},
                {'filters': {'$in': selected_brands}},
                {'filters': {'$in': selected_breeds}},
                {'filters': {'$in': selected_stages}},
                {'filters': category}]})
            
    if sort_by:
        products_data = products_data.sort('prices.0', int(sort_by))

    products = [Product(**product) for product in products_data]

    dog_brands = ['Royal Canin', 'Primens', 'Purina', 'YROVWENQ', 'CuteBone']
    dog_food_brands = ['Royal Canin', 'Purina']
    dog_accessories_brands = ['Primens', 'YROVWENQ', 'CuteBone']

    if category == 'dog':
        categories['brand'] = dog_brands
        if subcategory == 'accessories':
            categories['brand'] = dog_accessories_brands
        if subcategory == 'food':
            categories['brand'] = dog_food_brands

    cat_brands = ['Purina', 'Iams', 'On-Airstore', 'AIMICOCA', 'Catit']
    cat_food_brands = ['Purina', 'Iams']
    cat_accessories_brands = ['On-Airstore', 'AIMICOCA', 'Catit']

    if category == 'cat':
        categories['brand'] = cat_brands
        if subcategory == 'accessories':
            categories['brand'] = cat_accessories_brands
        if subcategory == 'food':
            categories['brand'] = cat_food_brands

    return render_template(
        'pets.html', title="PetPalz", categories=categories, category=category, 
        subcategory=subcategory, products=products, selected_categories=selected_categories
    )


@app.route('/search', methods=['GET', 'POST'])
def search():
    sort_by = None
    selected_categories = []
    categories = {
        'price': ['Up to $25', '$25 to $50', '$50 to $100', 'More than $100'],
        'brand': ['Purina', 'Iams', 'On-Airstore', 'AIMICOCA', 'Catit', 
                  'Royal Canin', 'Primens', 'YROVWENQ', 'CuteBone'],
        'breed': ['Large Breeds', 'Medium Breeds', 'Small Breeds'],
        'stage': ['Adult', 'Puppy', 'Senior']
    }

    search = request.args.get('query')
    search_query = search.lower().strip().split()
    products_data = app.db.products.find({'keywords': {'$all': search_query }})

    if request.method == 'POST':
        selected_prices = ['cat', 'dog']
        selected_brands = ['cat', 'dog']
        selected_breeds = ['cat', 'dog']
        selected_stages = ['cat', 'dog']

        sort_by = request.form.get('sortOrder')

        if 'category-price' in request.form:
            selected_prices = request.form.getlist('category-price')
        if 'category-brand' in request.form:
            selected_brands = request.form.getlist('category-brand')
        if 'category-breed' in request.form:
            selected_breeds = request.form.getlist('category-breed')
        if 'category-stage' in request.form:
            selected_stages = request.form.getlist('category-stage')
        selected_categories = selected_prices + selected_brands + selected_breeds + selected_stages

        products_data = app.db.products.find({
            '$and': [
            {'filters': {'$in': selected_prices}},
            {'filters': {'$in': selected_brands}},
            {'filters': {'$in': selected_breeds}},
            {'filters': {'$in': selected_stages}},
            {'keywords': {'$all': search_query}}]})
        
    if sort_by:
        products_data = products_data.sort('prices.0', int(sort_by))

    products = [Product(**product) for product in products_data]
    
    return render_template("search.html", title="PetPalz - Search", products=products, search=search.strip(), categories=categories, selected_categories=selected_categories)


@app.get("/product/<string:p>/rate")
@login_required
def rate_product(p):
    user_id = session["user_id"]
    rating = int(request.args.get("rating"))
    app.db.products.update_one({"title": p}, {"$set": {"rating." + str(user_id): rating}})

    return redirect(url_for("product", p=p))


@app.get('/cart/remove')
def delete_product():
    product_id = request.args.get('p')
    update = {"$unset": {f"cart.{product_id}": ""}}
    app.db.user.update_one({"_id": session["user_id"]}, update)
    
    return redirect(url_for('cart'))


@app.post('/cart/validate')
def validate_cep():
    cep = request.form.get('cep')
    url = f'https://viacep.com.br/ws/{cep}/json/'

    response = requests.get(url)
    if response:
        data = response.json()
    else:
        data = ['erro']

    if 'erro' in data:
        session['address'] = 'error'
        return  redirect(url_for('cart'))
    
    session['address'] = {
        'logradouro': data['logradouro'], 
        'bairro': data['bairro'], 
        'localidade': data['localidade'], 
        'uf': data['uf'], 
        'cep': data['cep']
    }

    return redirect(url_for('cart'))  

if __name__ == '__main__':
    app.run(debug=True)