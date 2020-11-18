import random
from flask import Flask, render_template, request, redirect, url_for
from scrapper import get_win

app = Flask(__name__)

db = []


@app.route("/")
def main():
    datas = db
    rnd, nums, bonus = get_win()
    win = {"rnd": rnd, "nums": nums, "bonus": bonus}
    return render_template("main.html", datas=datas, win=win)


@app.route("/add/")
def add():
    nums = list()
    while len(nums) < 6:
        num = random.randint(1, 45)
        if num not in nums:
            nums.append(num)
    nums.sort()
    db.append(nums)
    return redirect(url_for("main"))


if __name__ == "__main__":
    app.run(debug=True)