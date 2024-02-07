from flask import Flask, request, render_template, url_for, flash, redirect, session, abort, current_app
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
from flask_uploads import IMAGES, UploadSet, configure_uploads
import os
import secrets
from functools import wraps

from form import RegisterForm, LoginForm, AddProducts
from customer_form import CustomerRegisterForm, CustomerLoginForm
from datetime import datetime

from flask_msearch import Search
import json
from secrets import token_hex


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)



# uploading and saving images of products
app.config["UPLOADED_PHOTOS_DEST"] = os.path.join(basedir, "static/images")
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


# configure flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "customer login"
login_manager.needs_refresh_message_category = "danger"
login_manager.login_message = u"Login please!"


@login_manager.user_loader
def load_user(user_email):
    return db.get_or_404(User, user_email)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///e-commerce.db"
db = SQLAlchemy()
db.init_app(app)

search = Search()
search.init_app(app)



def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.email != "admin@email.com":
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


def user_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.email != CustomerUser.email:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function
# create user table for all admin registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True)
    username = db.Column(db.String(25), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


# for admin
class Brand(db.Model):
    __tablename__ = "Brand"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)


# for admin
class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)


# for admin
class AddProduct(db.Model):
    __tablename__ = "Add Products"
    __searchable__ = ['name', 'description']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    price = db.Column(db.Numeric(10,2), nullable=False)
    discount = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, nullable=False)
    colors = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    brand_id = db.Column(db.Integer, db.ForeignKey("Brand.id"),nullable=False)
    brand = db.relationship("Brand", backref=db.backref("brands", lazy=True))

    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    category = db.relationship("Brand", backref=db.backref("category", lazy=True))

    image_1 = db.Column(db.String(150), nullable=False, default="image.jpg")
    image_2 = db.Column(db.String(150), nullable=False, default="image.jpg")
    image_3 = db.Column(db.String(150), nullable=False, default="image.jpg")

    def __repr__(self):
        return '<AddProduct %r>' % self.name


class CustomerUser(UserMixin, db.Model):
    __tablename__ = "customeruser"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True)
    username = db.Column(db.String(25), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    country = db.Column(db.String(100))
    state = db.Column(db.String(100))
    city = db.Column(db.String(100))
    contact = db.Column(db.Integer)
    address = db.Column(db.String(100))
    zipcode = db.Column(db.Integer)
    profile = db.Column(db.String(150), nullable=False, default="image.jpg")

    def __repr__(self):
        return '<CustomerUser %r>' % self.name


class JsonEncodedDict(db.TypeDecorator):
    impl = db.Text
    def process_bind_param(self, value, dialect):
        if value is None:
            return {}
        else:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)


class CustomerOrder(db.Model):
    __tablename__ = "customerorder"
    id = db.Column(db.Integer, primary_key=True)
    invoice = db.Column(db.String(20))
    status = db.Column(db.String(20), default="pending")
    customer_id = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.now)
    orders = db.Column(JsonEncodedDict)

    def __repr__(self):
        return '<CustomerOrder %r>' % self.invoice


with app.app_context():
    db.create_all()


def brands_1():
    brands_1 = Brand.query.join(AddProduct, (Brand.id == AddProduct.brand_id)).all()
    return brands_1


def categories():
    categories = Category.query.join(AddProduct, (Category.id == AddProduct.category_id)).all()
    return categories


@app.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    products = AddProduct.query.filter(AddProduct.stock > 0).order_by(AddProduct.id.desc()).paginate(page=page, per_page=4)
    return render_template("products/index.html", products=products, brands_1=brands_1(), categories=categories())


@app.route("/result")
def result():
    searchword = request.args.get("q")
    products = AddProduct.query.msearch(searchword, fields=["name", "description"], limit=3)
    return render_template("products/result.html", brands_1=brands_1(), categories=categories())

@app.route("/product/<int:id>")
def single_page(id):
    product = AddProduct.query.get_or_404(id)

    return render_template("products/single_page.html", product=product,brands_1=brands_1(), categories=categories() )


@app.route("/brand/<int:b_id>")
def get_brand(b_id):
    page = request.args.get('page', 1, type=int)
    get_b = Brand.query.filter_by(id=b_id).first_or_404()
    brand = AddProduct.query.filter_by(brand_id=b_id).paginate(page=page, per_page=4)

    return render_template("products/index.html", brand=brand, brands_1=brands_1(),
                           categories=categories(), get_b=get_b)


@app.route("/category/<int:b_id>")
def get_category(b_id):
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(id=b_id).first_or_404()
    get_cat_prod = AddProduct.query.filter_by(category=get_cat).paginate(page=page, per_page=3)

    return render_template("products/index.html", get_cat_prod=get_cat_prod, categories=categories(),
                           brands_1=brands_1(), get_cat=get_cat)


@admin_only
@app.route("/admin")
def admin():
    products = AddProduct.query.all()
    return render_template("admin/index.html", title="admin", products=products)


@admin_only
@app.route("/brands")
def brands():
    brand = Brand.query.order_by(Brand.id.desc()).all()
    return render_template("admin/brand.html", title="Brand page", brands=brand)


@admin_only
@app.route("/category")
def category():
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template("admin/brand.html", title="Category page", categories=categories)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():

        result = (db.session.execute(db.select(User).where(User.email == form.email.data)))
        user = result.scalar()

        if user:
            flash("User with same email already exists, please login to continue")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(form.password.data,
                                                          method="pbkdf2:sha256",
                                                          salt_length=8)

        new_user = User(
            name =form.name.data,
            username= form.username.data,
            email= form.email.data,
            password= hash_and_salted_password,
        )

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('login'))
    return render_template("register.html", form=form, current_user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if form.validate and request.method == "POST":
        user = (db.session.execute(db.select(User).where(User.email == form.email.data))).scalar()
        if not user:
            flash("your email does not exists")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password= form.password.data):
            flash("password doesn't match login again!")
            return redirect(url_for("login"))
        else:
            login_user(user)
            flash("Successfully logged in!", "success")
            return redirect(url_for("admin"))
    return render_template("login.html", form=form, current_user=current_user)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("admin"))


@app.route("/add_brand", methods=["GET", "POST"])
@admin_only
def add_brand():
    if request.method == "POST":
        get_brand = request.form.get("brand")
        brand = Brand(name=get_brand)
        db.session.add(brand)
        flash(f"the brand {get_brand} was added to your store", "success")
        db.session.commit()
        return redirect(url_for("add_brand"))
    return render_template("products/add_brand.html", brands="brand")

@admin_only
@app.route("/update_brand/<int:id>", methods=["GET", "POST"])
def update_brand(id):
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get("brand")
    if request.method == "POST":
        updatebrand.name = brand
        flash(f"your brand {brand} has been updated", "success")
        db.session.commit()
        return redirect(url_for("brands"))
    return render_template("products/update_brand.html", title="update brand", updatebrand=updatebrand)


@admin_only
@app.route("/delete_brand/<int:p_id>", methods=["POST"])
def delete_brand(p_id):
    brand = Brand.query.get_or_404(p_id)
    if request.method == "POST":
        db.session.delete(brand)
        db.session.commit()
        flash(f"The brand {brand.name} has been removed", "success")
        return redirect(url_for("admin"))
    flash(f"The brand {brand.name} can't be removed", "warning")
    return redirect(url_for("admin"))


@app.route("/add_category", methods=["GET", "POST"])
@admin_only
def add_category():
    if request.method == "POST":
        get_category = request.form.get("category")
        category = Category(name=get_category)
        db.session.add(category)
        flash(f"the category {get_category} was added to your store", "success")
        db.session.commit()
        return redirect(url_for("add_brand"))
    return render_template("products/add_brand.html")


@admin_only
@app.route("/update_category/<int:id>", methods=["GET", "POST"])
def update_category(id):
    updatecat = Category.query.get_or_404(id)
    category = request.form.get("category")
    if request.method == "POST":
        updatecat.name = category
        flash(f"your brand {category} has been updated", "success")
        db.session.commit()
        return redirect(url_for("category"))
    return render_template("products/update_brand.html", title="update category", updatecategory=updatecat)


@admin_only
@app.route("/delete_category/<int:p_id>", methods=["POST"])
def delete_category(p_id):
    category = Category.query.get_or_404(p_id)
    if request.method == "POST":
        db.session.delete(category)
        db.session.commit()
        flash(f"The category {category.name} has been removed", "success")
        return redirect(url_for("admin"))
    flash(f"The category {category.name} can't be removed", "warning")
    return redirect(url_for("admin"))


@app.route("/add_product", methods=["GET", "POST"])
@admin_only
def add_product():
    brands = Brand.query.all()
    categories = Category.query.all()

    form = AddProducts(request.form)
    if request.method == "POST":
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        description = form.description.data
        colors = form.colors.data
        brand = request.form.get("brand")
        category = request.form.get("category")

        image_1 = photos.save(request.files.get("image_1"), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get("image_2"), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get("image_3"), name=secrets.token_hex(10) + ".")

        add_products = AddProduct(name=name, price=price, discount=discount,stock=stock,description=description,
                                  colors=colors, brand_id=brand, category_id=category, image_1=image_1, image_2=image_2,image_3=image_3)
        db.session.add(add_products)
        db.session.commit()
        flash(f"the product {name} has been added to your database", "success")
        return redirect(url_for("admin"))

    return render_template("products/addproduct.html", form=form, title="Add_products",
                           brands=brands, categories=categories)


@admin_only
@app.route("/update_product/<int:p_id>", methods=["GET", "POST"])
def update_product(p_id):
    brands = Brand.query.all()
    categories = Category.query.all()
    product = AddProduct.query.get_or_404(p_id)

    brand = request.form.get("brand")
    category = request.form.get("category")

    form = AddProducts(request.form)

    if request.method == "POST":
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.brand_id = brand
        product.category_id = category
        product.stock = form.stock.data
        product.colors = form.colors.data
        product.description = form.description.data

        if request.files.get("image_1"):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get("image_1"), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get("image_1"), name=secrets.token_hex(10) + ".")

        if request.files.get("image_2"):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                product.image_2 = photos.save(request.files.get("image_2"), name=secrets.token_hex(10) + ".")
            except:
                product.image_2 = photos.save(request.files.get("image_2"), name=secrets.token_hex(10) + ".")

        if request.files.get("image_3"):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                product.image_3 = photos.save(request.files.get("image_3"), name=secrets.token_hex(10) + ".")
            except:
                product.image_3 = photos.save(request.files.get("image_3"), name=secrets.token_hex(10) + ".")

        db.session.commit()
        flash(f"your product {product.name} is updated", "success")
        return redirect(url_for("admin"))

    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.colors.data = product.colors
    form.description.data = product.description

    return render_template("/products/update_product.html", title="update product", form=form,
                           brands=brands, categories=categories, product=product)


@admin_only
@app.route("/delete_product/<int:p_id>", methods=["POST"])
def delete_product(p_id):
    product = AddProduct.query.get_or_404(p_id)
    if request.method == "POST":
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
        except Exception as e:
            print(e)

        db.session.delete(product)
        db.session.commit()
        flash(f"The product {product.name} has been removed", "success")
        return redirect(url_for("admin"))
    flash(f"The product {product.name} can't be removed", "warning")
    return redirect(url_for("admin"))


def merge_dicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1+dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False


@app.route("/add_cart", methods=["GET", "POST"])
def add_cart():
    try:
        product_id=request.form.get("product_id")
        quantity = request.form.get("quantity")
        colors = request.form.get("colors")
        product = AddProduct.query.filter_by(id=product_id).first()
        if product_id and quantity and colors and request.method == "POST":
            DictItems = {product_id:{'name': product.name, 'price': product.price, 'discount': product.discount,
                                     'color': colors, 'quantity': quantity, 'image': product.image_1,
                                     'colors': product.colors}}

            if 'ShoppingCart' in session:
                print(session['ShoppingCart'])
                if product_id in session['ShoppingCart']:
                    for key, item in session["ShoppingCart"].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item["quantity"] += 1
                else:
                    session['ShoppingCart'] = merge_dicts(session['ShoppingCart'], DictItems)
                    return redirect(request.referrer)
            else:
                session['ShoppingCart'] = DictItems
                return redirect(request.referrer)
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)


@app.route("/carts")
def get_cart():
    if 'ShoppingCart' not in session or len(session["ShoppingCart"]) <= 0:
        return redirect(url_for("home"))
    subtotal=0
    grandtotal=0
    for key, product in session["ShoppingCart"].items():
        discount = (product['discount']/100) * float(product['price'])
        subtotal += float(product['price']) * int(product['quantity'])
        subtotal -= discount
        tax = ("%.2f" % (.06 * float(subtotal)))
        grandtotal = float("%.2f" %(1.06 * subtotal))
    return render_template("products/carts.html", tax=tax, grandtotal=grandtotal,
                           brands_1=brands_1(), categories=categories())


@app.route("/update_cart/<int:code>", methods=["GET", "POST"])
def update_cart(code):
    if "ShoppingCart" not in session or len(session["ShoppingCart"]) <= 0:
        return redirect(url_for("home"))
    if request.method == "POST":
        quantity = request.form.get("quantity")
        color = request.form.get("color")
        try:
            session.modified = True
            for key, item in session["ShoppingCart"].items():
                if int(key) == code:
                    item['quantity'] = quantity
                    item['color'] = color
                    flash(f"items updated!", 'success')
                    return redirect(url_for("get_cart"))
        except Exception as e:
            print(e)
            return redirect(url_for("get_cart"))


@app.route("/delete_item/<int:d_id>")
def delete_item(d_id):
    if "ShoppingCart" not in session or len(session["ShoppingCart"]) <= 0:
        return redirect(url_for("home"))

    try:
        session.modified = True
        for key, item in session["ShoppingCart"].items():
            if int(key) == d_id:
                session["ShoppingCart"].pop(key, None)
                flash(f"item deleted!", 'success')
                return redirect(url_for("get_cart"))
    except Exception as e:
        print(e)
        return redirect(url_for("get_cart"))


@app.route("/clear_cart")
def clear_cart():
    try:
        session.pop("ShoppingCart", None)
        return redirect(url_for("home"))
    except Exception as e:
        print(e)

@app.route("/empty_cart")
def empty_cart():
    try:
        session.clear()
        return redirect(url_for("home"))
    except Exception as e:
        print(e)


@app.route('/user_register', methods=["GET", "POST"])
def user_register():
    form = CustomerRegisterForm(request.form)
    if request.method == "POST" and form.validate():

        result = (db.session.execute(db.select(CustomerUser).where(CustomerUser.email == form.email.data)))
        user = result.scalar()

        if user:
            flash("User with same email already exists, please login to continue")
            return redirect(url_for('user_login'))

        hash_and_salted_password = generate_password_hash(form.password.data,
                                                          method="pbkdf2:sha256",
                                                          salt_length=8)

        new_user = CustomerUser(
            name =form.name.data,
            username= form.username.data,
            email= form.email.data,
            password= hash_and_salted_password,
            country = form.country.data,
            state= form.state.data,
            city= form.city.data,
            contact=form.contact.data,
            address=form.address.data,
            zipcode=form.zipcode.data,
            profile=form.profile.data,
        )

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('user_login'))
    return render_template("customer/register.html", form=form, current_user=current_user)

@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    form = CustomerLoginForm(request.form)
    if form.validate and request.method == "POST":
        user = (db.session.execute(db.select(CustomerUser).where(CustomerUser.email == form.email.data))).scalar()
        if not user:
            flash("your email does not exists")
            return redirect(url_for("user_login"))
        elif not check_password_hash(user.password, password= form.password.data):
            flash("password doesn't match login again!")
            return redirect(url_for("user_login"))
        else:
            login_user(user)
            flash("Successfully logged in!", "success")
            return redirect(url_for("home"))
    return render_template("customer/login.html", form=form, current_user=current_user)


@app.route("/user_logout")
def user_logout():
    logout_user()
    return redirect(url_for("home"))


@user_only
@app.route("/get_order")
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        try:
            order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session["ShoppingCart"])
            db.session.add(order)
            db.session.commit()
            session.pop("ShoppingCart")
            flash(f"order placed", "success")
            return redirect(url_for("home"))
        except Exception as e:
            print(e)
            flash(f"something went wrong ", "danger")
            return redirect(url_for("get_cart"))


@user_only
@app.route("/orders/<invoice>")
def orders(invoice):
    if current_user.is_authenticated:
        customer_id = current_user.id
        customer = CustomerUser.query.filter_by(id=customer_id).first
        orders= CustomerOrder.query.filter_by(customer_id=customer_id).first
        subtotal = 0
        grandtotal = 0
        for key, product in orders.orders.items():
            discount = (product['discount'] / 100) * float(product['price'])
            subtotal += float(product['price']) * int(product['quantity'])
            subtotal -= discount
            tax = ("%.2f" % (.06 * float(subtotal)))
            grandtotal = float("%.2f" % (1.06 * subtotal))


if __name__ == "__main__":
    app.run(debug=True)