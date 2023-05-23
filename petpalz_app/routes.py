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
    
@pages.route('/<category>')
@pages.route('/<category>/<subcategory>')
def pets(category, subcategory=None):
    if subcategory:
        products_data = current_app.db.products.find({'keywords': {'$all': [category, subcategory]}})
        products = [Product(**product) for product in products_data]
        print(products)
        return render_template('pets.html', title="PetPalz")
    else:
        products_data = current_app.db.products.find({'keywords': {'$all': [category]}})
        products = [Product(**product) for product in products_data]
        print(products)
        return render_template('pets.html', title="PetPalz")