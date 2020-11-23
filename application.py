import os
import random
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from scrapper import get_win

application = Flask(__name__)
application.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DB_URI", "mysql://root:1324@localhost/mydb"
)
csrf = CSRFProtect(application)
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
    user = db.Column(db.String(80))
    nums = db.Column(db.String(100))
    is_starred = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return "<Nums %r>" % self.nums


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
    if session is None:
        session["logged_in"] = False
    # 최근 당첨 번호 스크랩
    rnd, nums, bonus = get_win()
    win = {"rnd": rnd, "nums": nums, "bonus": bonus}
    # 로그인 여부 확인
    try:
        user = session["user"]
    except:
        user = "anonymous"
    # 로그인 ID로 get_data from database
    data = Nums.query.filter_by(user=user)
    data_list = list(data)
    data_list = data_list[-7:]
    datas = []
    for each in data_list:
        nums = each.nums
        nums_list = nums.split(",")
        nums_list = list(map(int, nums_list))
        datas.append([each.id, nums_list, each.is_starred])
    return render_template("main.html", datas=datas, win=win)


@application.route("/add/")
def add():
    try:
        user = session["user"]
    except:
        user = "anonymous"
    str_num = ",".join(list(map(str, get_nums())))
    new_num = Nums(user=user, nums=str_num)
    db.session.add(new_num)
    db.session.commit()
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
            hashed_password = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            new_user = User(username=username, password=hashed_password)
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
            data = User.query.filter_by(username=username).first()
            if bcrypt.checkpw(password.encode("utf-8"), data.password.encode("utf-8")):
                session["logged_in"] = True
                session["user"] = username
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
    session.pop("user", None)
    return redirect(url_for("main"))


@application.route("/starred/<id>")
def starred(id):
    data = Nums.query.filter_by(id=id).first()
    if data.is_starred == False:
        data.is_starred = True
    elif data.is_starred == True:
        data.is_starred = False
    db.session.commit()
    return redirect(request.referrer)


@application.route("/user/<username>")
def profile(username):
    user = username
    data = Nums.query.filter_by(user=user, is_starred=True)
    data_list = list(data)
    data_list = data_list[-7:]
    datas = []
    for each in data_list:
        nums = each.nums
        nums_list = nums.split(",")
        nums_list = list(map(int, nums_list))
        datas.append([each.id, nums_list, each.is_starred])
    return render_template("profile.html", datas=datas, user=user)


if __name__ == "__main__":
    application.debug = False
    db.create_all()
    application.secret_key = "randodlongkeys"
    application.run(
        host="0.0.0.0",
    )
