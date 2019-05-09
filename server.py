"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/register", methods=["GET"])
def register_form():

    return render_template("register_form.html")


@app.route("/register", methods=["POST"])
def register_process():

    email = request.form.get('email')
    password = request.form.get('password')

    if User.query.filter(User.email==email).first() == None:
        user = User(email=email, password=password)

        db.session.add(user)
        db.session.commit()
    else:
        flash('This user already exists.')

    return redirect("/")


@app.route("/login", methods=["GET"])
def login_form():

    return render_template("login_form.html")


@app.route("/login", methods=["POST"])
def login_process():

    email = request.form.get('email')
    password = request.form.get('password')

    user_query = User.query.filter(User.email == email, User.password == password).first()

    if user_query != None: 
        session["username"] = email
        flash('Logged in')
        user_id = user_query.user_id
        return redirect("/users/" + str(user_id))
    else: 
        flash('Username and password do not match.')
        return redirect("/login")


@app.route("/logout")
def logout_process():
    session.pop("username")
    return redirect("/")


@app.route("/users/<user_id>")
def user_details(user_id):

    user = User.query.get(user_id)

    return render_template("user_details.html",
                            user=user)

@app.route("/movies")
def movie_list():

    movies = Movie.query.order_by('title').all()
    return render_template("movie_list.html", movies=movies)


@app.route("/movies/<movie_id>")
def movie_details(movie_id):

    movie = Movie.query.get(movie_id)

    return render_template("movie_details.html",
                            movie=movie)


@app.route("/movies/<movie_id>", methods=["POST"])
def user_rating(movie_id):

    # Retrieve rating from form 
    rating = request.form.get('user_rating')

    # If logged in, get email to use in query
    email = session["username"]

    # Getting the user id with a query and getting user_id attribute
    user= User.query.filter(User.email == email).first()
    user_id = user.user_id

    # Querying for the user's rating 
    user_rating = Rating.query.filter(Rating.user_id == user_id, 
                                 Rating.movie_id == movie_id).first()

    # If the rating does not exist, add it to the ratings table and save 
    if user_rating == None: 
        user_rating = Rating(score=rating, user_id=user_id, movie_id=movie_id)

        db.session.add(user_rating)
        db.session.commit()
    # Else update the rating in the table and save 
    else:
        user_rating.score = rating
        db.session.commit()

    return redirect("/")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
