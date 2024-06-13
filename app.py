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

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

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


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    session.clear()
    if request.method == "POST":
        password = request.form.get("password")
        username = request.form.get("username")

        if not username:
            return render_template("sign-up.html", passer="Must enter a username")
        if not password:
            return render_template("sign-up.html", passer="Must enter a password")
            
        rows = SQL("SELECT * FROM users WHERE username == ?", username)

        if len(rows) != 0:
            return render_template("sign-up.html", userer="Username already exists")
            
        SQL("INSERT INTO users (username, hash) VALUES (?,?)", username, generate_password_hash(password))

        rows = SQL("SELECT * FROM users WHERE username == ?", username)

        session["user_id"] = rows[0][0]

        return redirect("/")
    else:
        return render_template("sign-up.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template("login.html", userer="Must enter a username")
        if not password:
            return render_template("login.html", passer="Must enter a password")
        
        rows = SQL("SELECT * FROM users WHERE username == ?", username)

        if not rows:
            return render_template("login.html", userer="User doesn't exist")

        if not check_password_hash(rows[0][2], password): # hash / password is at index 2
            return render_template("login.html", passer="Incorrect password")

        session["user_id"] = rows[0][0] # id is at index 0 
        return redirect("/")
    else:
        return render_template("login.html")
    
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")