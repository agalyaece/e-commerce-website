from flask import Flask, request, render_template, url_for, flash, redirect
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager,login_user, logout_user, current_user

from form import RegisterForm, LoginForm, AddProducts


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# configure flask login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///e-commerce.db"
db = SQLAlchemy()
db.init_app(app)


# create user table for all registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True)
    username = db.Column(db.String(25), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


class Brand(db.Model):
    __tablename__ = "Brand"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html", title="Home")


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
            return redirect(url_for("index"))
    return render_template("login.html", form=form, current_user=current_user)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/add_brand", methods=["GET", "POST"])
def add_brand():
    if request.method == "POST":
        get_brand = request.form.get("brand")
        brand = Brand(name=get_brand)
        db.session.add(brand)
        flash(f"the brand {get_brand} was added to your store", "success")
        db.session.commit()
        return redirect(url_for("add_brand"))
    return render_template("products/add_brand.html", brands="brand")


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        get_category = request.form.get("category")
        category = Brand(name=get_category)
        db.session.add(category)
        flash(f"the category {get_category} was added to your store", "success")
        db.session.commit()
        return redirect(url_for("add_brand"))
    return render_template("products/add_brand.html")


@app.route("add_product", methods=["GET", "POST"])
def add_product():
    form = AddProducts(request.form)
    return render_template("products/addproduct.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)