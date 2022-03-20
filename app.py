# Have changed the structure from what we discussed
# Removed the structure of "client" module and just added a common templates folder
# Made it like this to make the structure conform to what flask expects. Just a little less manual path specification
# But if the project grows bigger, we can change the structure to be more modular

from flask import Flask, render_template, redirect, url_for, request
from factory import object_factory

from db.home import home_handler
from db.user import user_handler
from db.level import level_handler
from db import database_handler

app = Flask(__name__)
app.secret_key = '21344'
object_factory.get_auth_object(app)
from api.auth import auth_router

app.register_blueprint(auth_router.auth_blueprint)


@app.before_first_request
def init():
    database_handler.setup()


@app.route("/")
def home_page():
    return "<h1>This is the homepage for the app</h1>"


@app.route("/home-feed")
def feed():
    data = request.json
    print("DATA: " + str(data))
    res = home_handler.get_home_feed(data)
    return render_template("home/home_template.html", res = res)


@app.route("/user/<id>")
def user(id):
    user_info = user_handler.get_user_info(id)
    user_levels = user_handler.get_user_levels(id)
    return render_template("profile/profile_template.html", userInfo = user_info, userLevels = user_levels)


@app.route("/level/<id>")
def level(id):
    level_info = level_handler.get_level_info(id)
    level_comments = level_handler.get_level_comments(id)
    return render_template("level/level_template.html", levelInfo = level_info, levelComments = level_comments)


@app.route("/add-comment", methods = ['POST'])
def add_comment():
    data = request.form
    level_handler.add_level_comment(data)
    return redirect(url_for("level", id = data['levelId']))


@app.route("/update-comment", methods = ['PATCH'])
def update_comment():
    data = request.form
    level_handler.update_level_comment(data)
    return redirect(url_for("level", id = data['levelId']))


@app.route("/delete-comment", methods = ['DELETE'])
def delete_comment():
    data = request.form
    level_handler.delete_comment(data)
    return redirect(url_for("level", id = data['levelId']))


@app.route("/update-level", methods = ['PATCH'])
def update_level():
    data = request.form
    level_handler.update_level(data)
    return redirect(url_for("level", id = data['levelId']))


@app.route("/delete-level", methods = ['DELETE'])
def delete_level():
    data = request.form
    level_handler.delete_level(data)
    return redirect(url_for("home_page"))


@app.route("/add-level", methods = ['POST'])
def add_level():
    data = request.form
    level_handler.add_level(data)
    return redirect(url_for("home_page"))


@app.route("/update-user", methods = ['PATCH'])
def update_user():
    data = request.form
    user_handler.update_user(data)
    return redirect(url_for("user", id = data["userId"]))


if __name__ == '__main__':
    app.run()
