from flask import Flask, flash, redirect, render_template, request, session, g
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
import time
import sqlite3


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DB = "data.db"

def create_connection(db_file):
    """ Create a connection to the sql database
    Parameters: 
    db_file - The name of the file
    Returns: A connection to the database
    """
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except sqlite3.Error as e:
        print(e)
    return None


def SQL(*args):
    query = str(args[0])

    conditions = []
    if len(args) > 0:
        for i in range(0, len(args), 1):
            if i != 0:
                conditions.append(args[i])

    conn = create_connection(DB)
    cur = conn.cursor()
    cur.execute(query, tuple(conditions))
    result = cur.fetchall()
    conn.commit()
    conn.close()
    return result

def login_required(f):
    """
    Decorate routes to require login.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

@app.route("/", methods=["GET", "POST"])
def index():
        return render_template("index.html")


@app.route("/sign-up")
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email:
            return render_template("register.html", passer="Must enter a email")
        if not password:
            return render_template("register.html", passer="Must enter a password")
        
        rows = SQL("SELECT * FROM users WHERE username == ?", email)

        if len(rows) != 0:
            return render_template("register.html", userer="Email already in use")
        
        SQL("INSERT INTO users (username, hash) VALUES (?,?)", email, generate_password_hash(password))

        rows = SQL("SELECT * FROM users WHERE username == ?", email)

        session["user_id"] = rows[0]["id"]

        return redirect("/")
    else:
        return render_template("sign-up.html")
    
@app.route("/login")
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email:
            return render_template("login.html")
        if not password:
            return render_template("login.html")

        rows = SQL("SELECT * FROM users WHERE username == ?", email)

        if not rows:
            return render_template("index.html")

        if not check_password_hash(rows[0]["hash"]):
            return render_template("index.html")

        session["user_id"] = rows[0]["id"]

        return redirect("/")
    else:
        return render_template("login.html")