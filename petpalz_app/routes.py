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


@pages.route("/")
def home():
    return render_template("home.html", title="PetPalz - Home")


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
