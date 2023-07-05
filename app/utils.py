import functools
from flask import request, redirect, session, current_app, url_for

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))

        return route(*args, **kwargs)

    return route_wrapper


def update_amount(product_id):
        product_amount = request.form.get('value')
        if not product_amount: product_amount = '1'
        current_app.db.user.update_one(
            {'_id': session["user_id"]}, 
            {'$set': {'cart.' + str(product_id) : int(product_amount)}}
        )