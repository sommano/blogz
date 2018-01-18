from flask import Flask, request, redirect,render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import cgi
import os

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://build-a-blog:easypassword@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route("/", methods = ["POST", "GET"])
def index():
    blogs = Blog.query.order_by(Blog.id.desc()).all()
    return render_template("blog.html", blogs = blogs)

@app.route("/newpost", methods = ["POST", "GET"])
def newpost():
    return render_template("newpost.html")

@app.route("/blog", methods = ["POST", "GET"])
def blog():
    someid = request.args.get("id")
    if someid:
        blog = Blog.query.filter_by(id=someid).first()
        return render_template("blogpost.html", blog=blog)
    else:
        blogs = Blog.query.order_by(Blog.id.desc()).all()
        return render_template("blog.html", blogs = blogs)

@app.route("/validate", methods=["POST", "GET"])
def validate():
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
        newpost = Blog(blogtitle, blogbody)
        db.session.add(newpost)
        db.session.flush()
        db.session.commit()

    currentid = newpost.id
    return redirect("/blog?id={0}".format(currentid))


if __name__ == '__main__':
    app.run()
