from flask import Flask, request, redirect,render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import cgi
import os

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://blogz:easypassword@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "secretkey"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship("Blog", backref = "owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ["login", "index", "signup", "blog", "static" ]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")

def verify(username, password, verify_password):
    if username == "":
        flash('Enter a username that is not blank', 'error')
        return False
    elif " " in username:
        flash('A space cannot be entered in the username', 'error')
        return False
    elif len(username) < 3:
        flash('Username cannot be less than 3 characters', 'error')
        return False

    elif len(password) < 3 or len(password) > 20:
        flash('Password must be between more than 3 characters and less than 20 characters', 'error')
        return False

    elif " " in password:
        flash('A space cannot be entered in the password', 'error')
        return False

    elif password != verify_password:
        flash('Password and verify password needs to be the same', 'error')
        return False
    elif password == "":
        flash('Enter a nonblank Password', 'error')
        return False

    elif " " in verify_password:
        flash('A space cannot be entered in the verify password', 'error')
        return False
    elif verify_password == "":
        flash('Enter a nonblank verified password', 'error')
        return False


    else:
        return True

@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("Incorrect username", "error")
            return redirect("/login")
        elif user and user.password == password:
            session["username"] = username
            flash("Logged In", "info")
            return redirect("/newpost")
        # elif user.username != username:
        #     flash("Incorrect username or password", "error")
        #     return redirect("/login", username=username)
        else:
            flash("Password does not match", "error")
            return redirect("/login")

    return render_template("login.html")



@app.route("/signup", methods = ["POST", "GET"])
def signup():
    # if request.method == "POST":
    #     username = request.form["username"]
    #     password = request.form["password"]
    #     verify = request.form["verify"]

        # if username == "":
        #     flash("Please enter a username")
        # elif password == "":
        #     flash("Please enter a password")
        # elif verify == "":
        #     flash("Please enter a verify password")
        # if not (len(password) >=3 or len(username)>=3):
        #     if not len(password) >= 3:
        #         flash("Please enter a username that is at least 3 characters long","error")
        #     if not len (username) >= 3:
        #         flash("Please enter a username that is at least 3 characters long","error")
        #
        # if not (username or password or verify):
        #     if not username:
        #         flash("Please enter a username", "error")
        #     if not password:
        #         flash("Please enter a password", "error")
        #     if not verify:
        #         flash("Please enter a matching password", "error")
        #     return redirect("/signup")
        # if not (password == verify):
        #     flash("Please enter a matching password", "error")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify']

        if verify(username, password, verify_password) == False:
            return render_template('signup.html', username=username)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('Username is already take, Please choose another', 'error')

    return render_template('signup.html')

    #     existing_user = User.query.filter_by(username=username).first()
    #     if not existing_user:
    #         new_user = User(username, password)
    #         db.session.add(new_user)
    #         db.session.commit()
    #         session["username"] = username
    #         return redirect("/newpost")
    #
    #     else:
    #         flash("Username already is taken","error")
    # return render_template("signup.html")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/", methods = ["POST", "GET"])
def index():
    users = User.query.all()
    return render_template("index.html", users=users)
    #return render_template("blog.html")

# @app.route("/index", methods = ["POST", "GET"])
# def index():
#     return render_template("index.html")

@app.route("/blog", methods = ["POST", "GET"])
def blog():
    #someid = request.args.get("id")
    #user = request.args.get("user")
    #blog =Blog.query.filter_by(id=someid).first()
    blogs = Blog.query.order_by("timestamp desc").all()
    return render_template("blog.html", blogs=blogs)

    # if someid != None:
    #     blog = Blog.query.get(someid)
    #     return render_template("blogpost.html", blog=blog)
    # if user != None:
    #     blogs = Blog.query.filter_by(id=someid).first()
    #     return render_template("singleUser.html", blogs = blogs)
    # return render_template("blog.html", blogs = Blog.query.all())

@app.route("/blogpost", methods = ["POST", "GET"])
def blogpost():
    num = request.args.get("id")
    user = request.args.get("user")
    blog =Blog.query.filter_by(id=num).first()

    return render_template("blogpost.html", blog=blog)

@app.route("/singleUser", methods = ["POST", "GET"])
def singleUser():
    id = request.args.get("id")
    #blog = Blog.query.get(someid)
    user_post = Blog.query.filter_by(user_id=id).all()
    user = User.query.filter_by(id=id).first()
    return render_template("singleUser.html", user_post=user_post, user=user)

@app.route("/newpost", methods = ["POST", "GET"])
def newpost():
    return render_template("newpost.html")

@app.route("/validate", methods=["POST", "GET"])
def validate():
    if not session:
        return redirect("login")

    owner = User.query.filter_by(username=session["username"]).first()
    blogtitle = request.form["blogtitle"]
    blogtitle_error = ""
    blogbody = request.form["blogbody"]
    blogbody_error = ""

    if blogtitle == "":
        blogtitle_error = "The blog title cannot be blank"
        return render_template("newpost.html", blogtitle=blogtitle, blogbody=blogbody, blogtitle_error = blogtitle_error, blogbody_error = blogbody_error)
#
    if blogbody == "":
        blogbody_error = "The blog text must contain an entry"
        return render_template("newpost.html", blogtitle=blogtitle, blogbody=blogbody, blogtitle_error = blogtitle_error, blogbody_error = blogbody_error)
#
    elif request.method == "POST":
        newpost = Blog(blogtitle, blogbody, owner)
        db.session.add(newpost)
        db.session.flush()
        db.session.commit()
        currentid = newpost.id
        return redirect("/blogpost?id={0}&user={1}".format(currentid,owner))

    return render_template('newpost.html')


if __name__ == '__main__':
    app.run()
