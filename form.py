from wtforms import Form, StringField, SubmitField, PasswordField, BooleanField, TextAreaField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileAllowed,FileField, FileRequired

 
# create from to register new user
class RegisterForm(Form):
    name = StringField("Name", validators=[Length(min=3, max=25), DataRequired(message="Please fill this field!")])
    username = StringField("UserName", validators=[Length(min=3,max=25), DataRequired(message="Please fill this field!")])
    email = StringField("email", validators=[Email(message="Please enter a valid email address"), DataRequired(message="Please fill this field!")])
    password = PasswordField("Password", validators=[Length(min=3,max=25),EqualTo(fieldname="confirm", message="Your password do not match") ,DataRequired(message="Please fill this field!")])
    confirm = PasswordField("Confirm Password", validators=[Length(min=3,max=25), DataRequired(message="Please fill this field!")])
    submit = SubmitField("submit!")


class LoginForm(Form):
    email = StringField("email", validators=[Length(min=8, max=50),Email(message="Please enter a valid email address"),
                                             DataRequired(message="Please fill this field!")])
    password = PasswordField("Password", validators=[Length(min=3, max=25),
                                                     DataRequired(message="Please fill this field!")])


class AddProducts(Form):
    name = StringField("Name", validators=[Length(min=3, max=25), DataRequired(message="Please fill this field!")])
    price = DecimalField("Price", validators=[DataRequired(message="Please fill this field!")])
    discount = IntegerField("Discount", default=0)
    stock = IntegerField("Stock", validators=[DataRequired(message="Please fill this field!")])
    description = TextAreaField("Description", validators=[DataRequired(message="Please fill this field!")])
    colors = TextAreaField("Colors", validators=[DataRequired(message="Please fill this field!")])

    image_1 = FileField("image_1", validators=[FileAllowed(["jpg", "png", "gif", "jpeg"])])

    image_2 = FileField("image_2", validators=[FileAllowed(["jpg", "png", "gif", "jpeg"])])

    image_3 = FileField("image_3", validators=[FileAllowed(["jpg", "png", "gif", "jpeg"])])

