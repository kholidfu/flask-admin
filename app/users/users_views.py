from flask import render_template, redirect, request, session, flash, url_for
from flask import Blueprint
from functools import wraps
from app.forms import AdminLoginForm, UserLoginForm, UserRegisterForm
import pymongo
from flask.ext.mail import Mail, Message
from app import app
import datetime
from itsdangerous import URLSafeSerializer, BadSignature
from flask_oauthlib.client import OAuth, OAuthException
from flask.ext.bcrypt import Bcrypt


# setup database mongo
try:
    c = pymongo.Connection("custom_etc_hosts.com")
except:
    c = pymongo.Connection()

dbusers = c["users"]  # nanti ada dbusers.user, dbusers.admin, dll

users = Blueprint('users', __name__, url_prefix="/users")

# encrypt password using bcrypt
bcrypt = Bcrypt(app)

# oauth

FACEBOOK_APP_ID = "1852267481665400"
FACEBOOK_APP_SECRET = "7c17448df181b87f82e1637f98946348"

TWITTER_KEY = "3GsBeQyAHqt4iEotdSnAOLm87"
TWITTER_SECRET = "RgAyw44xhNRH3ygkZ6sx5p8oHULs0TxoeQw8eRnN6Hzq2mJPLs"

oauth = OAuth(app)

facebook = oauth.remote_app(
    'facebook',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={"scope": "email"},
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    access_token_method="GET",
    authorize_url='https://www.facebook.com/dialog/oauth',
)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("email") is not None:
            return f(*args, **kwargs)
        else:
            flash("Please log in first...", "error")
            next_url = request.url
            login_url = "%s?next=%s" % (url_for("users.users_login"), next_url)
            return redirect(login_url)
    return decorated_function


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))


def get_serializer(secret_key=None):
    """serialize object for url confirmation."""
    if secret_key is None:
        secret_key = app.secret_key
    return URLSafeSerializer(secret_key)


def get_activation_link(user_email):
    s = get_serializer()
    payload = s.dumps(user_email)
    # return url_for("activate_user", payload=payload, _external=True)
    return payload


@users.route("/register", methods=["GET", "POST"])
def users_register():
    form = UserRegisterForm()
    mail = Mail(app)
    error = None
    twitter_name = request.args.get("tw")

    if request.method == "POST" and form.validate():
        # now, validation done in forms.py
        if dbusers.user.find_one({"email": form.email.data}):
            error = "Email sudah terdaftar!"
            return render_template("/users/register.html", form=form, error=error)
        else:
            # simpan session username
            session["email"] = form.email.data

            # cek apakah dia daftar menggunakan twitter
            if twitter_name:
                dbusers.user.update({"twitter_name": form.twitter_name.data}, {"$set": {
                    "firstname": form.firstname.data,
                    "lastname": form.lastname.data,
                    "password": bcrypt.generate_password_hash(form.password.data),
                    "email": form.email.data,
                    "joined": datetime.datetime.now(),
                    "confirmed": True,  # for email confirmation needs
                    "completed": True,
                }})
            else:
                # simpan data seperti biasa
                dbusers.user.insert({
                    "firstname": form.firstname.data,
                    "lastname": form.lastname.data,
                    "password": bcrypt.generate_password_hash(form.password.data),
                    "email": form.email.data,
                    "joined": datetime.datetime.now(),
                    "confirmed": False,  # for email confirmation needs
                    "completed": True,
                })
            # send email
            emailstring = """
            Thank you for registering with example.com.

            Here is your credential info, please keep it secret:

            username: %s
            password: %s
            confirmation url: http://127.0.0.1:5000/users/activate/%s

            Regards,

            laporpakdhe.org
            """ % (form.email.data, form.password.data, get_activation_link(form.email.data))
            msg = Message("Welcome to example.com", sender="info@example.com", recipients=[form.email.data])
            msg.body = emailstring
            # mail.send(msg)
            # return redirect(request.args.get("next") or url_for("users"))
            return redirect(request.args.get("next") or url_for("users.users_index"))
    else:
        flash_errors(form)

    return render_template("/users/register.html", form=form, twitter_name=twitter_name)


@users.route("/")
@login_required
def users_index():
    email = session["email"]
    data = dbusers.user.find_one({"email": email})
    # hanya mereka yang ber-email valid yg bisa masuk
    if not email:
        return redirect("/users/register")
            
    return render_template("/users/index.html", email=email, data=data)


@users.route("/activate/<payload>")
def activate_user(payload):
    """check if activation link is valid"""
    s = get_serializer()
    try:
        user_email = s.loads(payload)
    except BadSignature:
        abort(404)

    user = dbusers.user.find_one({"email": user_email})
    # user.activate()
    if user:
        if user["confirmed"]:
            flash("Users already activated!")
        else:
            dbusers.user.update({"email": user_email}, {"$set": {"confirmed": True}})
            flash("User activated!")
    else:
        abort(404)
    return redirect(url_for("index"))


@users.route("/login", methods=["GET", "POST"])
def users_login():
    form = UserLoginForm()
    error = None

    if request.method == "POST" and form.validate():
        user = dbusers.user.find_one({"email": form.email.data})
        
        session["email"] = form.email.data
        return redirect(request.args.get("next") or url_for("users.users_index"))
    else:
        flash_errors(form)

    return render_template("/users/login.html", form=form)

##########
### FB ###
##########

@app.route('/users/login/fb')
def users_loginfb():
    callback = url_for(
        'facebook_authorized',
        # next=request.args.get('next') or request.referrer or None,
        next=request.args.get('next'),
        _external=True
    )
    return facebook.authorize(callback=callback)


@app.route("/login/fb/authorized")
def facebook_authorized():
    resp = facebook.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message

    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')

    """ sample fb data
    from pprint import pformat
    return Response(pformat(me.data), mimetype='text/plain')

    {u'email': u'kh.fuadi@gmail.com',
    u'first_name': u'Kholid',
    u'gender': u'male',
    u'id': u'792786710817761',
    u'last_name': u'Fuadi',
    u'link': u'https://www.facebook.com/app_scoped_user_id/792786710817761/',
    u'locale': u'en_US',
    u'name': u'Kholid Fuadi',
    u'timezone': 7,
    u'updated_time': u'2015-04-24T01:51:57+0000',
    u'verified': True}
    """

    # store session first
    session["email"] = me.data["email"]

    # store global variable to be used in sidebar and menu header
    # g.profile_picture = me.data["id"]

    # insert email into database

    user = dbusers.user.find_one({"email": me.data["email"]})
    if not user:
        dbusers.user.insert({
            "email": me.data["email"], 
            "fbid": me.data["id"],
            "firstname": me.data["first_name"],
            "lastname": me.data["last_name"],
            "confirmed": True,
            "gender": me.data["gender"],
            "fbid": me.data["id"],
            "joined": datetime.datetime.now(),
            "completed": True,
        })

        # suruh lengkapi profil
        flash("Mohon lengkapi data Anda demi akurasi laporan.")
        return redirect(url_for("users.users_profile"))
    
    # from pprint import pformat
    # return Response(pformat(me.data), mimetype='text/plain')
    
    # return redirect(request.args.get("next"))
    return redirect(url_for("users.users_index"))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


###############
### Twitter ###
###############

twitter = oauth.remote_app(
    'twitter',
    consumer_key=TWITTER_KEY,
    consumer_secret=TWITTER_SECRET,
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
)


@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


@app.route('/users/login/twitter')
def users_logintw():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/users/twitter/oauthorized')
def oauthorized():
    """twitter user diredirect ke /users/register saja
    karena data yang disediakan twitter tidak se-komplit fb.
    """
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp

    """
    {'oauth_token': u'14355401-cSw2vYM4r6NAQGgC6Za3NYAu2E9DImNp8hmKbYBYI',
    'oauth_token_secret': u'NCWm1Muoph1xkRqdGxmMvHlo67hbIgsxsqj5hoRBhczxX',
    'screen_name': u'sopier',
    'user_id': u'14355401'}
    """
    user = dbusers.user.find_one({"twitter_name": resp["screen_name"]})
    # jika user sudah memasukkan email
    if user:
        if user.get("email"):
            session["email"] = user["email"]
    else:
        session["email"] = resp["screen_name"]

    # pake twython aje
    from twython import Twython
    t = Twython(
        app_key=TWITTER_KEY,
        app_secret=TWITTER_SECRET,
        oauth_token=resp["oauth_token"],
        oauth_token_secret=resp["oauth_token_secret"])

    twitterdata = t.show_user(screen_name="%s" % resp["screen_name"])
    twimgurl = twitterdata["profile_image_url"]

    # jika visitor dari twitter perlu ditandai dengan menyimpan screen_name
    # jika sudah ada, maka tidak perlu register lagi, langsung di redirect ke 
    # halaman profil
    # jika sudah lengkap email, nama depan, nama belakang dan password
    # jika completed == True: baru boleh lapor
    # pengguna fb completed = True
    # register biasa completed = True
    user = dbusers.user.find_one({"twitter_name": resp["screen_name"]})

    if not user:
        dbusers.user.insert({
            "twitter_name": twitterdata["screen_name"],
            "completed": False,
        })
        return redirect("/users/register?tw=%s" % resp["screen_name"])

    # from pprint import pformat
    # return Response(pformat(t.show_user(screen_name="%s" % resp["screen_name"])), mimetype='text/plain')
    
    # cek apakah email, firstname, lastname sudah terisi?
    # jika sudah bisa lapor, else ke profile
    if user.get("email") and user.get("firstname") and user.get("lastname"):
        return redirect("/users")
    return redirect("/users/profile")


@users.route("/profile", methods=["GET", "POST"])
@login_required
def users_profile():
    form = UserProfileForm()
    data = dbusers.user.find_one({"email": session.get("email")})

    # post validation and processing
    if request.method == "POST" and form.validate():
        email = form.email.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        password = form.password.data
        repassword = form.repassword.data
        telpon = "+62%s" % form.telpon.data
        gender = form.gender.data
        birth = form.birth.data
        nomid = form.nomid.data
        avatar = form.avatar.data

        # insert data into database
        # if from twitter
        if data.get("twitter_name"):
            if password == repassword:
                dbusers.user.update({"twitter_name": data["twitter_name"]}, {"$set": {
                    "email": email,
                    "firstname": firstname,
                    "lastname": lastname,
                    "password": password,
                    "telpon": telpon,
                    "gender": gender,
                    "birth": birth,
                    "nomid": nomid,
                    "completed": True,
                    "confirmed": True,
                    "avatar": avatar,
                }})
                # update session from twitter username to true email.
                session["email"] = dbusers.user.find_one({"email": email})["email"]

        # selain twitter, key-nya adalah email
        if password == repassword:
            dbusers.user.update({"email": session.get("email")}, {"$set": {
                "email": email,
                "firstname": firstname,
                "lastname": lastname,
                "password": password,
                "telpon": telpon,
                "gender": gender,
                "birth": birth,
                "nomid": nomid,
                "completed": True,
                "confirmed": True,
                "avatar": avatar,
            }})

        # return Response("""
        # email: %s
        # nama depan: %s
        # nama belakang: %s
        # telpon: %s
        # jenis kelamin: %s
        # tanggal lahir: %s
        # nomor identitas: %s
        # avatar: %s
        # """ % (email, 
        #        firstname, 
        #        lastname,
        #        telpon,
        #        gender,
        #        birth,
        #        nomid,
        #        avatar,
        #    ), mimetype="text/plain")
        flash("Data sudah berhasil diperbarui")
        return redirect("/users/profile")
    else:
        flash_errors(form)

    return render_template("users/profile.html", data=data, form=form)


@users.route("/logout")
def users_logout():
    if "email" not in session:
        return redirect(url_for("users_login"))
    session.pop("email", None)
    # print "popped out!"  # fixed
    return redirect(url_for("index"))



