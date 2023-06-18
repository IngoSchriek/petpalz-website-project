import functools
import uuid
from dataclasses import asdict
import requests
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    session,
    url_for,
    request,
    jsonify
)
from passlib.hash import pbkdf2_sha256
from petpalz_app.models import Product, User


from petpalz_app.forms import LoginForm, RegisterForm

pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))

        return route(*args, **kwargs)

    return route_wrapper


@pages.route("/update")
def update():
    old_products = current_app.db.new_products.find()
    new_products = []

    for product in old_products:
        product["_id"] = str(product["_id"])
        new_products.append(product)

    current_app.db.products.insert_many(new_products)

    return redirect(url_for("pages.home"))


@pages.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html", title="PetPalz - Home")



@pages.get("/product/<string:p>/rate")
@login_required
def rate_product(p):
    user_id = session["user_id"]
    rating = int(request.args.get("rating"))
    current_app.db.products.update_one({"title": p}, {"$set": {"rating." + str(user_id): rating}})

    return redirect(url_for(".product", p=p))


@pages.route("/register", methods=["POST", "GET"])
def register():
    if session.get("email"):
        return redirect(url_for(".home"))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            _id=uuid.uuid4().hex, 
            username=form.username.data,
            email=form.email.data, 
            password=pbkdf2_sha256.hash(form.password.data), 
        )                                                     

        current_app.db.user.insert_one(asdict(user))

        flash("User registered successfully", "success")
        return redirect(url_for(".login"))

    return render_template(
        "register.html", title="Pet Palz - Register", form=form
    )


@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".home"))

    form = LoginForm()
    if form.validate_on_submit():
        
        user_data = current_app.db.user.find_one({"email": form.email.data})

        if not user_data:
            flash("Login credentials not correct", category="danger")
            return redirect(url_for(".login"))

        user = User(**user_data)
        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            session["user_id"] = user._id
            session["email"] = user.email
            session["username"] = user.username
            session["address"] = None

            return redirect(url_for(".home"))

        flash("Login credentials not correct", category="danger")
        
    return render_template("login.html", title="Pet Palz - Login", form=form)




@pages.route("/logout")
@login_required
def logout():
    del session["username"]
    del session["email"]
    del session["user_id"]
    del session["csrf_token"]
    del session["address"]

    return redirect(url_for(".home"))


@pages.route("/product", methods=["GET", "POST"])
def product():
    product = Product(**(current_app.db.products.find_one({'title': request.args.get('p')})))
    category = product.filters[0]
    subcategory = product.filters[1]
    if request.method == "POST":
        if not session:
            return redirect(url_for('.login'))
        value = request.form.get('value')
        if not value: value = '1'
        current_app.db.user.update_one({'_id': session["user_id"]}, {'$set': {'cart.' + str(product._id) : int(value)}})
        return redirect(url_for('pages.cart'))
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


@pages.route("/cart/", methods=["GET", "POST"])
@login_required
def cart():
    if request.method == 'POST':
        value = request.form.get('value')
        if not value: value = '1'
        product_id = request.form.get('product_id')
        current_app.db.user.update_one({'_id': session["user_id"]}, {'$set': {'cart.' + str(product_id) : int(value)}})
        return redirect(url_for('.cart'))
    user = User(**(current_app.db.user.find_one({'_id': session["user_id"] })))
    products_ids = [str(product_id) for product_id in user.cart.keys()]
    products_data = current_app.db.products.find({'_id': {'$in': products_ids} })
    products = [Product(**product) for product in products_data]
    count = len(products)
    lst = []
    for product in products:
        lst += [(product.prices[0] * user.cart[product._id])]
    total = sum(lst)
    return render_template("cart.html", title="PetPalz - Cart", products=products, user=user, total=total, count=count)

@pages.get('/cart/remove')
def delete_product():
    product_id = request.args.get('p')
    update = {"$unset": {f"cart.{product_id}": ""}}
    current_app.db.user.update_one({"_id": session["user_id"]}, update)
    return redirect(url_for('.cart'))

@pages.post('/cart/validate')
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
        return  redirect(url_for('.cart'))
    session['address'] = {'logradouro': data['logradouro'], 'bairro': data['bairro'], 'localidade': data['localidade'], 'uf': data['uf'], 'cep': data['cep']}
    return redirect(url_for('.cart'))  



categories = {'price': ['Up to $25', '$25 to $50', '$50 to $100', 'More than $100'],
              'brand': ['Purina', 'Iams', 'On-Airstore', 'AIMICOCA', 'Catit'] + ['Royal Canin', 'Primens', 'YROVWENQ', 'CuteBone'],
              'breed': ['Large Breeds', 'Medium Breeds', 'Small Breeds'],
              'stage': ['Adult', 'Puppy', 'Senior']}

@pages.route('/add')
def add():
    title = "Iams Proactive Health Playful Kitten 7lbs"
    current_app.db.products.insert_one({
  "title": title,
  "prices": [
    38.00,
    "51.40",
    ""
  ],
  "rating": 0,
  "description": "blabla",
  "img": "CatFood7",
  "keywords": [word.strip(",").lower() for word in title.split(' ')],
  "filters": [
    "cat",
    "food",
    "Iams",
    "Puppy",
    "$25 to $50",
    "Medium Breeds"
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
    cbrands = ['Purina', 'Iams', 'On-Airstore', 'AIMICOCA', 'Catit']
    cfbrands = ['Purina', 'Iams']
    cabrands = ['On-Airstore', 'AIMICOCA', 'Catit']
    if category == 'cat':
        categories['brand'] = cbrands
        if subcategory == 'accessories':
            categories['brand'] = cabrands
        if subcategory == 'food':
            categories['brand'] = cfbrands
    return render_template('pets.html', title="PetPalz", categories=categories, category=category, subcategory=subcategory, products=products, selected_categories=selected_categories)



@pages.route('/search', methods=['GET', 'POST'])
def search():
    sort_by = None
    selected_categories = []
    categories = {'price': ['Up to $25', '$25 to $50', '$50 to $100', 'More than $100'],
              'brand': ['Purina', 'Iams', 'On-Airstore', 'AIMICOCA', 'Catit'] + ['Royal Canin', 'Primens', 'YROVWENQ', 'CuteBone'],
              'breed': ['Large Breeds', 'Medium Breeds', 'Small Breeds'],
              'stage': ['Adult', 'Puppy', 'Senior']}
    search = request.args.get('query')
    search_query = search.lower().strip().split()
    products_data = current_app.db.products.find({'keywords': {'$all': search_query}})
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
        products_data = current_app.db.products.find({
            '$and': [
            {'filters': {'$in': selected_prices}},
            {'filters': {'$in': selected_brands}},
            {'filters': {'$in': selected_breeds}},
            {'filters': {'$in': selected_stages}},
            {'keywords': {'$all': search_query}}]})
    if sort_by:
        sort_by = int(sort_by)
        products_data = products_data.sort('prices.0', sort_by)
    products = [Product(**product) for product in products_data]
    
    return render_template("search.html", title="PetPalz - Search", products=products, search=search.strip(), categories=categories, selected_categories=selected_categories)