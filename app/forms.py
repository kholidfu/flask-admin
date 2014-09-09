from flask_wtf import Form
from wtforms import BooleanField, TextField, TextAreaField, SubmitField, validators, ValidationError, PasswordField
from flask import flash
import pymongo


class AdminLoginForm(Form):
    email = TextField("Email", [validators.Required("Please enter your Email.")])
    password = PasswordField("Password", [validators.Required("Please enter your password.")])
    submit = SubmitField("Login")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        if "kinanti@gmail.com" == self.email.data and "delapan" == self.password.data:
            return True
        else:
            self.email.errors.append("Invalid username or password")
            return False

class UserLoginForm(Form):
    email = TextField("Email", [validators.Required("Please enter your Email.")])
    password = PasswordField("Password", [validators.Required("Please enter your password.")])
    submit = SubmitField("Login")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            print "not validated!"
            return False

        if "sopier@gmail.com" == self.email.data and "delapan" == self.password.data:
            return True
        else:
            self.email.errors.append("Invalid username or password")
            return False

class UserRegisterForm(Form):
    username = TextField("Username", [validators.Required("Please enter your Username.")])
    email = TextField("Email", [validators.Required("Please enter your Email.")])
    password = PasswordField("Password", [validators.Required("Please enter your password.")])
    submit = SubmitField("Login")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            print "not validated!"
            return False

        # validasi: dilihat apakah username sudah ada di database atau belum
        # dilihat apakah email sudah terdaftar atau belum
        if "user" == self.username.data and "user@gmail.com" == self.email.data and "delapan" == self.password.data:
            return True
        else:
            self.email.errors.append("Invalid username or password")
            return False
        
