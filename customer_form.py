from wtforms import Form, StringField, SubmitField, PasswordField, BooleanField, TextAreaField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileAllowed,FileField, FileRequired

class CustomerRegisterForm(Form):
    name = StringField("Name", validators=[Length(min=3, max=25), DataRequired(message="Please fill this field!")])
    username = StringField("UserName",
                           validators=[Length(min=3, max=25), DataRequired(message="Please fill this field!")])
    email = StringField("email", validators=[Email(message="Please enter a valid email address"),
                                             DataRequired(message="Please fill this field!")])
    password = PasswordField("Password", validators=[Length(min=3, max=25),
                                                     EqualTo(fieldname="confirm", message="Your password do not match"),
                                                     DataRequired(message="Please fill this field!")])
    confirm = PasswordField("Confirm Password",
                            validators=[Length(min=3, max=25), DataRequired(message="Please fill this field!")])
    country = StringField("Country",validators=[DataRequired(message="Please fill this field!")])
    state = StringField("State",validators=[Length(min=3, max=25), DataRequired(message="Please fill this field!")])
    city = StringField("City", validators=[Length(min=3, max=25), DataRequired(message="Please fill this field!")])
    contact = IntegerField("Contact",validators=[DataRequired(message="Please fill this field!")])
    address = StringField("Address",validators=[Length(min=3, max=100), DataRequired(message="Please fill this field!")])
    zipcode = IntegerField("zipcode",validators=[DataRequired(message="Please fill this field!")])
    profile = FileField("Profile", validators=[FileAllowed(["jpg", "png", "gif", "jpeg"],
                                                           "Image only please")])
    submit = SubmitField("Register!")

class CustomerLoginForm(Form):
    email = StringField("email",
                            validators=[Length(min=8, max=50), Email(message="Please enter a valid email address"),
                                        DataRequired(message="Please fill this field!")])
    password = PasswordField("Password", validators=[Length(min=3, max=25),
                                                         DataRequired(message="Please fill this field!")])

