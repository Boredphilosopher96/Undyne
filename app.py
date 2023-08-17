import json
import os

import pydantic
from dotenv import load_dotenv, find_dotenv
from flask import Flask, render_template, redirect, url_for, request, session, jsonify, abort

import auth_router
import utils
from db import database_handler
from db.home import home_handler
from db.level import level_handler, level_models
from db.level.level_models import CommentData
from db.user import user_handler
from factory import object_factory
from firebase_handler import Firebase
from level_data_model import LevelData

load_dotenv(find_dotenv())

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.secret_key = os.getenv("APP_SECRET")
object_factory._create_auth_object(app)

app.register_blueprint(auth_router.auth_blueprint)
firebase_object = Firebase()

with app.app_context():
    database_handler.setup()


@app.route("/")
def home_page():
    return redirect(url_for("feed"))


@app.route("/home-feed")
def feed():
    # data = request.get_json(force = True)
    data = request.data
    if request.data:
        res = home_handler.get_homefeed_with_filters(data)
    else:
        res = home_handler.get_homefeed()
    return render_template("home/home_template.html", res = res)


@app.route("/search", methods = ["POST"])
def feed_search():
    data = request.get_json()
    if data:
        res = home_handler.get_homefeed_with_filters(data)
    else:
        res = home_handler.get_homefeed()
    return render_template("home/search_results.html", res = res)


@app.route("/game")
def game():
    debug_enabled = False
    
    user_id = session.get("profile")
    if user_id is not None:
        user_id = user_id.get("user_id")
    
    level_id = request.args.get("id")
    if level_id is None or not level_id.isdigit():
        return render_template("game/game.html", level_data_dict = "", difficulty = "", debug = debug_enabled)
    
    level_info = level_handler.get_level_info(level_id)
    
    if len(level_info) != 1:
        return render_template("game/game.html", level_data_dict = "", difficulty = "", debug = debug_enabled)
    
    level_info = level_info[0]
    level_is_public = level_info[6]
    level_user = level_info[7]
    
    if not level_is_public and level_user != user_id:
        return render_template("game/game.html", level_data_dict = "", difficulty = "", debug = debug_enabled)
    
    level_data_dict = level_info[4]
    difficulty = level_info[5]
    
    return render_template(
        "game/game.html", level_data_dict = level_data_dict, difficulty = difficulty, debug = debug_enabled
    )


@app.route("/user/<id>")
def user(id):
    user_info = user_handler.get_user_info(id)
    if user_info:
        user_levels = user_handler.get_user_levels(user_info[0][0])
        level_count = len(user_levels)
        return render_template(
            "profile/profile_template.html", user_info = user_info, user_levels = user_levels, level_count = level_count
        )
    else:
        abort(404)


@app.route("/level/<level_id>")
def level(level_id):
    level_info = level_handler.get_level_info(level_id)
    level_is_public = level_info[0][6]
    
    if not level_is_public:
        abort(404)
    
    level_comments = level_handler.get_level_comments(level_id)
    level_commenters = [comment[1] for comment in level_comments]
    return render_template(
        "level/level_template.html", levelInfo = level_info, levelComments = level_comments,
        commenters = level_commenters
    )


@app.route("/replace-comment", methods = ["POST"])
@utils.requires_auth
def replace_comment():
    user_id = session.get("profile")
    if user_id is not None:
        user_id = user_id.get("user_id")

    level_id = request.form.get("level")
    level_info = level_handler.get_level_info(level_id)[0]
    
    level_is_public = level_info[6]
    level_user = level_info[7]
    
    comment_data = CommentData(
        **{
            "userId": user_id,
            "commentBody": request.form.get("comment"),
            "levelId": level_id,
            "commentRating": request.form.get("rating")
        }
    )
    
    if level_is_public and user_id is not None and user_id != level_user:
        level_handler.add_level_comment(comment_data)
    
    return redirect(url_for("level", level_id = level_id))


@app.route("/update-comment", methods = ["PATCH"])
@utils.requires_auth
def update_comment():
    user_id = session.get("profile").get("user_id")
    comment_data = CommentData(
        **{
            "commentId": request.form.get("comment_id"),
            "userId": user_id,
            "commentBody": request.form.get("comment"),
            "levelId": request.form.get("level_id"),
            "commentRating": request.form.get("rating")
        }
    )
    
    level_handler.update_level_comment(comment_data)
    return jsonify({"result": "success"})


@app.route("/delete-comment", methods = ["DELETE"])
@utils.requires_auth
def delete_comment():
    user_id = session.get("profile")
    if user_id is not None:
        user_id = user_id.get("user_id")
    
    comment_id = request.form.get('commentId')
    level_id = request.form.get('levelId')
    
    comment_info = level_handler.get_comment_info(comment_id)[0]
    comment_user = comment_info[3]
    
    if user_id is not None and user_id == comment_user:
        level_handler.delete_comment(comment_id, level_id)
    return jsonify({"result": "success"})


@app.route("/level-creator/")
@utils.requires_auth
def level_creator():
    if session["profile"]["user_id"] is None:
        return redirect(url_for('home'))
    level_id = request.args.get("id")
    session["level_id"] = None
    if level_id is not None:
        level_data = level_handler.get_level_info(level_id)
        if session["profile"]["user_id"] != level_data[0][7]:
            return redirect(url_for('home'))
        
        session["level_id"] = level_id
        send = level_data[0]["level_description"]
        send["title"] = level_data[0]["level_name"]
        send["description"] = level_data[0]["level_summary"]
        send["difficulty"] = level_data[0]["level_diff"]
        send["isPublic"] = level_data[0]["level_published"]
    else:
        send = {
            "title": "Untitled",
            "description": "Add a description",
            "difficulty": "easy",
            "isPublic": False,
            "attacks": []
        }
    
    return render_template(
        "level_creator/level_creator.html", level_json = send, is_new_level = level_id is None,
        user_name = session['profile']['user_name']
    )


@app.route("/update-level", methods = ['PATCH'])
@utils.requires_auth
def update_level():
    current_level_data = level_handler.get_level_info(session['level_id'])
    
    if session['profile']['user_id'] != current_level_data[0][7]:
        return redirect(url_for('home'))
    
    client_level_data = request.get_json()
    try:
        level_data = LevelData(**client_level_data)
    except pydantic.ValidationError as e:
        response = str(e).replace("(type=value_error)", "")
        return jsonify(response = response)
    
    attacks = {
        "attacks": client_level_data['attacks']
    }
    update = {
        "levelId": session['level_id'],
        "levelName": level_data.title,
        "levelRating": current_level_data[0]['level_rating'],
        "levelSummary": level_data.description,
        "levelDescription": json.dumps(attacks),
        "levelDiff": level_data.difficulty,
        "levelPublished": level_data.is_public
    }
    level_handler.update_level(level_models.LevelData(**update))
    response = "Saved!"
    return jsonify(response = response)


@app.route("/delete-level", methods = ['DELETE'])
@utils.requires_auth
def delete_level():
    level_id = request.args.get("id")
    level_data = level_handler.get_level_info(level_id)
    if session['profile']['user_id'] != level_data[0][7]:
        return redirect(url_for('home'))
    
    level_handler.delete_level(level_id)
    return session['profile']


@app.route("/add-level", methods = ['POST'])
@utils.requires_auth
def add_level():
    client_level_data = request.get_json()
    try:
        level_data = LevelData(**client_level_data)
    except pydantic.ValidationError as e:
        response = str(e).replace("(type=value_error)", "")
        return jsonify(response = response)
    
    add = {
        "user_id": session['profile']['user_id'],
        "levelName": level_data.title,
        "levelRating": 0,
        "levelSummary": level_data.description,
        "levelDescription": json.dumps(
            {
                "attacks": client_level_data['attacks']
            }
        ),
        "levelDiff": level_data.difficulty,
        "levelPublished": level_data.is_public
    }
    session['level_id'] = level_handler.add_level(level_models.LevelData(**add))[0]
    return jsonify(
        response = "Saved!",
        level_url = url_for("level_creator", id = session['level_id'])
    )


@app.route("/update-user", methods = ['PATCH'])
@utils.requires_auth
def update_user():
    data = request.get_json()
    user_handler.update_user_avatar(data)
    return redirect(url_for("user", id = data["userId"]))


@app.route("/get-upload-path", methods = ['GET'])
@utils.requires_auth
def get_upload_path():
    file_type = request.args.get('fileType')
    if file_type not in {'png', 'jpeg'}:
        abort(403)
    return firebase_object.get_signed_url(
        file_name = f"{session['profile']['user_name']}_pfp.jpeg", file_type = file_type
    )


@app.route("/upload-completed", methods = ["POST"])
@utils.requires_auth
def upload_completed():
    file_url = firebase_object.get_file_url(file_name = f"{session['profile']['user_name']}_pfp.jpeg")
    user_handler.update_user_avatar(file_url)
    session['profile']['user_avatar'] = file_url
    return redirect(url_for("user", id = session['profile']['user_id']))


@app.errorhandler(404)
def resource_not_found(e):
    data = {
        "error_code": 404,
        "error_message": "Resource Not Found! "
    }
    return render_template("error/error.html", data = data)


@app.errorhandler(403)
def forbidden_resource(e):
    data = {
        "error_code": 403,
        "error_message": "Page Forbidden! "
    }
    return render_template("error/error.html", data = data)


@app.errorhandler(500)
def server_error(e):
    data = {
        "error_code": 500,
        "error_message": "Server error!"
    }
    return render_template("error/error.html", data = data)


@app.errorhandler(502)
def bad_gateway(e):
    data = {
        "error_code": 502,
        "error_message": "Bad Gateway!"
    }
    return render_template("error/error.html", data = data)


if __name__ == '__main__':
    app.config["TRAP_HTTP_EXCEPTIONS"] = True
    app.register_error_handler(404, resource_not_found)
    app.register_error_handler(403, forbidden_resource)
    app.register_error_handler(500, server_error)
    app.register_error_handler(502, bad_gateway)
    
    app.run()
