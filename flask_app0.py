from flask import Flask, flash, redirect, render_template, request, session, abort, json, jsonify, send_from_directory
from functools import wraps
import os

app = Flask(__name__, instance_path="C:/Users/drumman22/Documents/GitHub/bhop-bot-flask/")

# functions
def r_append_file(file, data):
    with open(file, "a") as f:
        f.write(data)

# decorators
def require_login(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if session.get("logged_in"):
            return function(*args, **kwargs)
        else:
            return render_template("login.html")
    return wrapper

def require_appkey(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if request.headers.get("key") == "KEY":
            return function(*args, **kwargs)
        else:
            r_append_file(os.path.join(app.instance_path, "protected/local/addr.txt"), "ERROR: 401 UNAUTHORIZED USER\nMETHOD: {}\nUSER AGENT: {}\nIP ADDR: {}\n\n".format(request.method, request.environ["HTTP_USER_AGENT"], request.environ.get("HTTP_X_REAL_IP", request.remote_addr)))
            return home()
    return wrapper


# routes
@app.route("/")
@require_login
def home():
    # return "Welcome to your homepage, {}!".format(session.get("username"))
    return render_template("homepage.html")


@app.route("/login", methods=["POST"])
def login():
    if session.get("logged_in"):
        return home()
    elif request.form["password"] == "password" and request.form["username"] == "admin":
        session["logged_in"] = True
        session["username"] = request.form["username"]
    return home()

@app.route("/botlogs/<file_name>")
@require_login
def botlogs(file_name):
    print(app.root_path)
    try:
        return send_from_directory(os.path.join(app.instance_path, "protected/botlogs"), file_name)
    except Exception as e:
        print(e)
        return home()

@app.route("/api/v1/<path:file_name>/", methods=["GET", "POST"])
@app.route("/api/v1/<path:file_name>/<file_mode>", methods=["POST"])
@require_appkey
def api_file(file_name, file_mode="w"):
    filename = os.path.join(app.instance_path, "protected/" + file_name)
    if request.method == "POST":
        try:
            if request.content_type == "application/json":
                data = request.get_json(silent=True)
                with open(filename, file_mode) as f:
                    json.dump(data, f)
            elif request.content_type == "text/plain":
                data = request.get_data()
                print(data)
                with open(filename, file_mode) as f:
                    f.write(data.decode("utf-8"))
            return jsonify({"okay": "passed"})
        except Exception as e:
            return jsonify({"error": e})
    elif request.method == "GET":
        try:
            with open(filename) as f:
                return f.read()
        except Exception as e:
            return jsonify({"error": e})


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(port=805, debug=False)
