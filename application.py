import random
from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask import Flask, render_template, request, redirect, url_for, session
from scrapper import get_win

application = Flask(__name__)
application.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:1324@localhost/mydb"
db = SQLAlchemy(application)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80), unique=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Nums(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("users", lazy=True))
    # nums 구현 필!!!

    def __repr__(self):
        return "<Nums %r>" % self.name


def get_nums():
    nums = list()
    while len(nums) < 6:
        num = random.randint(1, 45)
        if num not in nums:
            nums.append(num)
    nums.sort()
    return nums


@application.route("/")
def main():
    rnd, nums, bonus = get_win()
    win = {"rnd": rnd, "nums": nums, "bonus": bonus}
    return render_template("main.html", datas=datas, win=win)


datas = []


@application.route("/add/")
def add():
    datas.append(get_nums())
    return redirect(url_for("main"))


@application.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_cfm = request.form["password_cfm"]

        if not (username and password and password_cfm):
            return "모두 작성해주세요."
        if password != password_cfm:
            return "비밀번호를 다시 확인해주세요."
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))

    return render_template("register.html")


@application.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            data = User.query.filter_by(username=username, password=password).first()
            if data is not None:
                session["logged_in"] = True
                return redirect(url_for("main"))
            else:
                return "Can't log in, Please re-check username & password."
        except:
            return "Can't log in, Please re-check username & password."
    else:
        return render_template("login.html")


@application.route("/logout")
def logout():
    session["logged_in"] = False
    return redirect(url_for("main"))


if __name__ == "__main__":
    application.debug = True
    db.create_all()
    application.secret_key = "randodlongkeys"
    application.run(
        host="0.0.0.0",
    )
