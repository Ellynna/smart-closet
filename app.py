from flask import Flask, render_template
import json
import sys
import os

application = Flask(__name__, static_folder='static')
# @application.route("/")
# def hello():
#     return render_template("home.html")

# @application.route("/")
# def hello():
#     return render_template("closet.html")

@application.route("/")
def index():
    return render_template("index.html")

@application.route("/closet")
def closet():
    return render_template("closet.html")

@application.route("/closet_1")
def closet_1():
    #filenames = os.listdir('static/images/c1')
    with open('clothes.json') as cloth_json:
        json_data = json.load(cloth_json)
        box1_data = json_data["closet"][0]
    return render_template("closet_1.html",result=box1_data)



# @application.route("/closet_detail")
# def closet_detail():
#     return render_template("closet_detail.html")


if __name__ == "__main__":
    application.run(host='0.0.0.0')
