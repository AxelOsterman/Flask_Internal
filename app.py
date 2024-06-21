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

search_req = ""

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

@app.route("/search", methods=["POST"])
def search():
    global search_req
    if request.method == "POST":
        search_req = request.form.get("search")
        fetched_data = SQL("SELECT Name, City, Country, Latitude, Longitude FROM airports")
        matches_search = False
        refined_data = []

        for data in fetched_data: # Loop through all the data that is in the database
            for i in range(0, 5): # Check the Name, City and Country, Longitude, Latitude section
                matches_search = True
                data_chars = []
                for character in str(data[i]):
                    data_chars.append(character)
                counter = 0
                for char in search_req: # Loop through every character in "data" and check if it matches that of the users search
                    if len(data_chars) >= len(search_req):
                        if data_chars[counter].lower() != char.lower(): # Set to lower so there's not captilisation errors
                            matches_search = False
                    else:
                        matches_search = False
                    counter += 1
                if matches_search == True:
                        refined_data.append(data)
        if len(refined_data) <= 0:
            return render_template("error.html", error="Unable to find your request", errorCode="404 Not Found")
        else:
            return render_template("destinations.html", fetched_data=refined_data)


@app.route("/destinations")
def destinations():
    global search_req
    refined_data = []
    fetched_data = SQL("SELECT Name, City, Country, Latitude, Longitude FROM airports")
    field = request.args.get('field')
    sort = request.args.get('sort')

    if field in ['Name', 'City', 'Country', 'Latitude', 'Longitutde']:
        if sort == 'a-z':
            fetched_data = SQL(f"SELECT Name, City, Country, Latitude, Longitude FROM airports ORDER BY {field} ASC")
        else:
            fetched_data = SQL(f"SELECT Name, City, Country, Latitude, Longitude FROM airports ORDER BY {field} DESC")

    for data in fetched_data: # Loop through all the data that is in the database
        for i in range(0, 5): # Check the Name, City and Country, Longitude, Latitude section
            matches_search = True
            data_chars = []
            for character in str(data[i]):
                data_chars.append(character)
            counter = 0
            for char in search_req: # Loop through every character in "data" and check if it matches that of the users search
                if len(data_chars) >= len(search_req):
                    if data_chars[counter].lower() != char.lower(): # Set to lower so there's not captilisation errors
                        matches_search = False
                else:
                    matches_search = False
                counter += 1
            if matches_search == True:
                    refined_data.append(data)
    search_req = "" # reset search request so user can return to original destination page if they refresh the page
    if len(refined_data) <= 0:
        return render_template("error.html", error="Unable to find your request", errorCode="404 Not Found")
    else:
        return render_template("destinations.html", fetched_data=refined_data)
    
@app.route("/bookings", methods=["GET", "POST"])
@login_required
def bookings():
    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("bookings.html")
    
@app.route("/manage-booking", methods=["GET", "POST"])
@login_required
def manage_bookings():
    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("manage-bookings.html")
        
    
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("contact.html")
    
@app.route("/error")
def error():
    return render_template("error.html")