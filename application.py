import os
import requests
import json

from flask import Flask, session, render_template, request, redirect, g, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from functools import wraps


#CLAVE PARA ACCEDER A GOODREADERS
KEY = "GOv5GE123S6v9stJnks7BA"

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response

# Route to the index
@app.route("/")
def index():
    return render_template("index.html")

# Logout function
@app.route("/log_out")
def log_out():
    session.clear()
    return render_template("index.html")

# Route to the search after login 
@app.route("/login", methods=["POST"])
def login():        
    if request.method == "GET":
        return render_template("error.html", message="Please login with username and password.")
    else:
        # Store the id of the current session
        username = request.form.get("username")
        user = db.execute("SELECT * FROM user_library WHERE username = :username",{"username": username}).fetchone()
        
        if user is None:
            return render_template("error.html", message="The user is not register.")

        session["user_id"] = user.id

        return redirect(url_for('search'))

#Route to the register page
@app.route("/register")
def register():
    return render_template("register.html")

#Route to the search page
@app.route("/search")
@login_required
def search():
       
    # Get the all the books values
    books = db.execute("SELECT * FROM book").fetchall()
    search_options = ["ISBN","Title", "Author"]
    
    return render_template("search.html",books=books,search_options=search_options)

#Route to the search page after the registration
@app.route("/new_register", methods=["POST"])
def new_register():
    """insert a new user in the table and log in"""

    # Get form information.
    username = request.form.get("username")
    password = request.form.get("password")

    user_info = db.execute("SELECT * FROM user_library WHERE username = :username", {"username": username}).fetchone()
    # Make sure user not exists.
    if user_info is not None:
        return render_template("error.html", message="The username is already used.")

    #Insert the new user if he/she does not exits    
    db.execute("INSERT INTO user_library (username, password) VALUES (:username, :password)",
            {"username": username, "password": password})
    db.commit()
    
    # Store the id of the current session
    user = db.execute("SELECT * FROM user_library WHERE username = :username",{"username": username}).fetchone()
    session["user_id"] = user.id
        
    return redirect(url_for('search'))


#Route to search page with new information list of books
@app.route("/filter_books", methods=["POST"])
def filter_books():
    
    """Filter the book by search"""
    if request.method != "POST":
        return render_template("error.html", message="First Login with your username.")
    else:
        
        #according to the selected field, we did a search
        book_field = request.form.get("book_field")
        book_field = book_field.lower()
        field_value = request.form.get("field_value")
        field_value = '%' + field_value + '%'

        stmt =  "SELECT * FROM book WHERE " + book_field +" LIKE :field_value"

        filter_books = db.execute(stmt, {"book_field":book_field , "field_value":field_value}).fetchall()
        

        # Get the all the books values
        books = db.execute("SELECT * FROM book").fetchall()
        search_options = ["ISBN","Title", "Author"]
        
        return render_template("search.html", books=books, filter_books = filter_books,search_options=search_options)
    
#Render the informaton of one book
@app.route("/filter_books/<int:book_id>")
def book_info(book_id):
    """ List the book deatails"""
    
    #Get the info of the book
    book = db.execute("SELECT * FROM book WHERE id = :book_id",{"book_id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message = "No such Book.")

    #Get all the reviews joined with the name of each user
    stmt = "SELECT user_library.*, reviewer.* FROM user_library INNER JOIN reviewer ON user_library.id=reviewer.id_user WHERE id_book = :book_id"
    reviews = db.execute(stmt,{"book_id": book_id}).fetchall()

    #Get the user_review info
    user_review = db.execute("SELECT * FROM reviewer WHERE id_book = :book_id AND id_user = :user_id",
        {"book_id": book_id, "user_id": session["user_id"]}).fetchone()

    #If this info not exist we could add a comment, else we can not.
    is_commented = True
    if user_review is None:
        is_commented = False

    #Proccess for rating count of Goofreaders
    goodreader_info = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": book.isbn })
    goodreader_info = goodreader_info.json()
    goodreader_info = goodreader_info["books"]

    average_rating = goodreader_info[0]["average_rating"]
    ratings_counts = goodreader_info[0]["ratings_count"]

    return render_template("book_info.html",book=book, reviews = reviews, is_commented = is_commented
    , average_rating = average_rating, ratings_counts = ratings_counts )

@app.route("/submit_comment/<int:book_id>", methods=["GET","POST"])
def submit_comment(book_id):
    """ Insert a new comment with score"""
    
    #Information for inserting
    score = request.form.get("score")
    comment = request.form.get("comment")

    if score is None or comment is None:
        return render_template("error.html",message="Please submit the complete information.")

    #Inserte a new review
    db.execute("INSERT INTO reviewer (id_book, id_user, comment, score_user) VALUES (:id_book, :id_user, :comment, :score_user)",
            {"id_book":book_id, "id_user":session["user_id"], "comment": comment, "score_user": score})
    
    db.commit()

    #Get the info of the book
    book = db.execute("SELECT * FROM book WHERE id = :book_id",{"book_id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message = "No such Book.")

    #Get the reviews joined with the name of the user
    stmt = "SELECT user_library.*, reviewer.* FROM user_library INNER JOIN reviewer ON user_library.id=reviewer.id_user WHERE id_book = :book_id"
    reviews = db.execute(stmt,{"book_id": book_id}).fetchall()

    #Get the user_review info
    user_review = db.execute("SELECT * FROM reviewer WHERE id_book = :book_id AND id_user = :user_id",
        {"book_id": book_id, "user_id": session["user_id"]}).fetchone()

    #If this info not exist we could add a comment, else we can not.
    is_commented = True
    if user_review is None:
        is_commented = False

    #Insert a new score if a new comment is introduced
    average_score = db.execute("SELECT AVG(score_user) FROM reviewer WHERE id_book = :book_id",{"book_id":book_id}).fetchone()
    average_score = average_score.items()
    average_score = average_score[0]
    average_score = float(average_score[1])

    db.execute("UPDATE book SET score = :average_score WHERE id = :book_id", {"average_score":average_score, "book_id": book_id})        
    db.commit()

    #Get the info of the book
    book = db.execute("SELECT * FROM book WHERE id = :book_id",{"book_id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message = "No such Book.")

    #Proccess for rating count of Goofreaders
    goodreader_info = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": book.isbn })
    goodreader_info = goodreader_info.json()
    goodreader_info = goodreader_info["books"]

    average_rating = goodreader_info[0]["average_rating"]
    ratings_counts = goodreader_info[0]["ratings_count"]

    return render_template("book_info.html",book=book, reviews = reviews, is_commented = is_commented
    , average_rating = average_rating, ratings_counts = ratings_counts )


@app.route("/api/<int:book_id>", methods=["GET"])
def api(book_id):
    #own database info
    book = db.execute("SELECT * FROM book WHERE id = :book_id",{"book_id": book_id}).fetchone()
    
    if book is None:
        return render_template("error.html",message="404 error. Resource not found.")

    #Proccess for rating count of Goofreaders
    goodreader_info = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": book.isbn })
    goodreader_info = goodreader_info.json()
    goodreader_info = goodreader_info["books"]

    average_rating = goodreader_info[0]["average_rating"]
    ratings_counts = goodreader_info[0]["ratings_count"]
  
    new_dict = {}
    new_dict["title"] = book.title
    new_dict["author"] = book.author
    new_dict["year"] = book.year
    new_dict["isbn"] = book.isbn
    new_dict["review_count"] = ratings_counts
    new_dict["average_score"] = average_rating

    return json.dumps(new_dict)