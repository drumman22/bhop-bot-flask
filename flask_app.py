from flask import Flask, request, json, jsonify, abort, render_template
from functools import wraps

app = Flask(__name__)

# The actual decorator function
def require_appkey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get("key") and request.headers.get("key") == "KEY_GOES_HERE":
            return view_function(*args, **kwargs)
        else:
            return abort(401)
            render_template("401.html")
    return decorated_function

def r_append_file(file, data):
    with open(file, "a") as f:
        f.write(data)

# routes

@app.route("/api/<file_name>", methods=["GET", "POST"])
@require_appkey
def method_file_name(file_name):
    if request.method == "POST":
        try:
            data = request.get_json(silent=True)
            with open(file_name, "w") as f:
                json.dump(data, f)
            return jsonify({"okay": "passed"})
        except:
            return abort(404)
    if request.method == "GET":
        try:
            with open(file_name) as f:
                return f.read()
        except:
            abort(404)

@app.route("/api/ip")
@require_appkey
def get_ip():
    return jsonify({"ip": request.environ["REMOTE_ADDR"]})


# error handles

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(401)
def unauthorized(e):
    r_append_file("addr.txt", "ERROR: 401 UNAUTHORIZED USER\nMETHOD: {}\nUSER AGENT: {}\nIP ADDR: {}\n\n".format(request.method, request.environ["HTTP_USER_AGENT"], request.environ.get("HTTP_X_REAL_IP", request.remote_addr)))
    return render_template("401.html")


if __name__ == "__main__":
    app.run(port=80, debug=False)
