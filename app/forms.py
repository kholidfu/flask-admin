from flask_wtf import Form
from wtforms import TextField, SubmitField, validators, PasswordField, BooleanField, FileField
import pymongo
from flask.ext.bcrypt import Bcrypt
from app import app


# encrypt mod
bcrypt = Bcrypt(app)

# set you username and password for admin here:
username = "admin@admin.com"
password = "password"

# dbase things
try:
    c = pymongo.Connection("laporpakdhe.org")
except:
    c = pymongo.Connection()
dbusers = c["users"]


class AdminLoginForm(Form):
    email = TextField("Email", [validators.Required("Please enter your Email.")])
    password = PasswordField("Password", [validators.Required("Please enter your password.")])
    submit = SubmitField("Login")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        if username == self.email.data and password == self.password.data:
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
        user = dbusers.user.find_one({"email": self.email.data})

        if user:
            # retrieve password data
            pwdhash = user["password"]
            m = bcrypt.check_password_hash(pwdhash, self.password.data)

            if not m:
                # convert into list
                self.password.errors = list(self.password.errors)
                self.password.errors.append("Password tidak cucok!")
                # convert back to tuple
                self.password.errors = tuple(self.password.errors)
                return False
        else:
            # username tidak terdaftar
            # convert into list
            self.email.errors = list(self.email.errors)
            self.email.errors.append("Email tidak terdaftar!")
            # convert back to tuple
            self.email.errors = tuple(self.email.errors)
            return False

        return True


class UserRegisterForm(Form):
    firstname = TextField("Firstname", [
        validators.Length(min=4, max=25),
        validators.Required(message="Mohon masukkan nama depan Anda")
    ])
    lastname = TextField("Lastname")
    email = TextField("Email", [validators.Required("Please enter your Email.")])
    password = PasswordField("Password", [
        validators.Required("Please enter your password."),
        validators.EqualTo("repassword", message="Password must match!")
    ])
    repassword = PasswordField("Repeat Password")
    twitter_name = TextField("Twitter name")
    accept_terms = BooleanField("I accept the TOS", [validators.Required()])
    submit = SubmitField("Login")


    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)


    def validate(self):
        user = dbusers.user.find_one({"email": self.email.data})
        if user:
            # convert into list
            self.email.errors = list(self.email.errors)
            self.email.errors.append("Email sudah terdaftar")
            # convert back to tuple
            self.email.errors = tuple(self.email.errors)
            return False

        return True


class UserProfileForm(Form):
    email = TextField("Email", [validators.Required("Please enter your email.")])
    firstname = TextField("Firstname", [validators.Required("Please enter your Username.")])
    lastname = TextField("Lastname", [validators.Required("Please enter your lastname.")])
    password = PasswordField("Password", [validators.Required("Please enter your password.")])
    repassword = PasswordField("Repassword", [validators.Required("Please confirm your password.")])
    telpon = TextField("No telepon")
    gender = TextField("Jenis kelamin")
    birth = TextField("Tgl Lahir")
    nomid = TextField("Nomer identitas")
    avatar = FileField()
    submit = SubmitField("Login")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)


class UserCommentForm(Form):
    """
    Ini form untuk user comment
    """
    comment = TextField("Comment", [
        validators.Length(min=4, max=200),
        validators.Required("Komentar tidak boleh kosong")])
    submit = SubmitField("Kirim komentar")


    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
