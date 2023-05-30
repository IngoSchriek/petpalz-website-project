import functools
import uuid

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    session,
    url_for,
    request,
)
from passlib.hash import pbkdf2_sha256
from petpalz_app.models import Product
from uuid import uuid4

pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

# def login_required(route):
#     @functools.wraps(route)
#     def route_wrapper(*args, **kwargs):
#         if session.get("email") is None:
#             return redirect(url_for(".login"))

#         return route(*args, **kwargs)

#     return route_wrapper


@pages.route("/", methods=["GET", "POST"])
def home():

    return render_template("home.html", title="PetPalz - Home")


@pages.route('/search')
def search():
    search_query = request.args.get('query').lower().strip().split()
    products_data = current_app.db.products.find({'keywords': {'$all': search_query}})
    products = [Product(**product) for product in products_data]
    return render_template("search.html", title="PetPalz - Search", products=products)

@pages.route("/product")
def product():
    return render_template("product.html", title="PetPalz - Product")


@pages.route("/login")
def login():
    return render_template("login.html", title="PetPalz - Login")


@pages.route("/logout")
def logout():
    return None


@pages.route("/register")
def register():
    return render_template("register.html", title="PetPalz - Register")


@pages.route("/cart")
def cart():
    return render_template("cart.html", title="PetPalz - Cart")

categories = {'price': ['Up to $25', '$25 to $50', '$50 to $100', 'More than $100'],
              'brand': [],
              'breed': ['Large Breeds', 'Medium Breeds', 'Small Breeds'],
              'stage': ['Adult', 'Puppy', 'Senior']}

@pages.get("/favicon.ico")
def favicon():
    return None

@pages.route('/add')
def add():
    title = "Purina ONE Natural Dry Cat Food, Tender Selects Blend With Real Salmon - 7 lb. Bag"
    current_app.db.products.insert_one({
  "title": title,
  "prices": [
    24.59,
    37.89,
    ""
  ],
  "rating": 0,
  "specification": "blabla",
  "description": "blabla",
  "img": "CatFood4",
  "keywords": [word.strip(",").lower() for word in title.split(' ')],
  "filters": [
    "cat",
    "food",
    "Purina",
    "Adult",
    "Up to $25",
    "Medium Breeds",
    "Small Breeds"
  ]
})
    return redirect('/cat')

@pages.route('/<category>', methods=['GET', 'POST'])
@pages.route('/<category>/<subcategory>', methods=['GET', 'POST'])
def pets(category, subcategory=None):
    category = category
    subcategory = subcategory
    sort_by = None
    selected_categories = []
    if subcategory:
        products_data = current_app.db.products.find({'filters': {'$all': [category, subcategory]}})
    else:
        products_data = current_app.db.products.find({'filters': {'$all': [category]}})
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
            products_data = current_app.db.products.find({
                '$and': [
                {'filters': {'$in': selected_prices}},
                {'filters': {'$in': selected_brands}},
                {'filters': {'$in': selected_breeds}},
                {'filters': {'$in': selected_stages}},
                {'filters': {'$all': [category, subcategory]}}]})
        else:
            products_data = current_app.db.products.find({
                '$and': [
                {'filters': {'$in': selected_prices}},
                {'filters': {'$in': selected_brands}},
                {'filters': {'$in': selected_breeds}},
                {'filters': {'$in': selected_stages}},
                {'filters': category}]})
    if sort_by:
        sort_by = int(sort_by)
        products_data = products_data.sort('prices.0', sort_by)
    products = [Product(**product) for product in products_data]
    dbrands = ['Royal Canin', 'Primens', 'Purina', 'YROVWENQ', 'CuteBone']
    dfbrands = ['Royal Canin', 'Purina']
    dabrands = ['Primens', 'YROVWENQ', 'CuteBone']
    if category == 'dog':
        categories['brand'] = dbrands
        if subcategory == 'accessories':
            categories['brand'] = dabrands
        if subcategory == 'food':
            categories['brand'] = dfbrands
    cbrands = ['Purina', 'Iams', 'On-Airstore' 'AIMICOCA']
    cfbrands = ['Purina', 'Iams']
    cabrands = ['On-Airstore', 'AIMICOCA']
    if category == 'cat':
        categories['brand'] = cbrands
        if subcategory == 'accessories':
            categories['brand'] = cabrands
        if subcategory == 'food':
            categories['brand'] = cfbrands
    return render_template('pets.html', title="PetPalz", sort_by=sort_by, categories=categories, category=category, subcategory=subcategory, products=products, selected_categories=selected_categories)

