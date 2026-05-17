from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_login import login_required
from flask_login import logout_user
from flask_login import current_user
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

import json
import os
from datetime import datetime

app = Flask(__name__)

app.secret_key = "supersecretkey"

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

BOOKS_FILE = "books.json"


if not os.path.exists(BOOKS_FILE):

    with open(BOOKS_FILE, "w") as file:

        json.dump([], file)


class User(UserMixin):

    def __init__(self, id, username, password):

        self.id = id

        self.username = username

        self.password = password


users = {

    "admin": {

        "password":
        generate_password_hash("admin123")
    },

    "student": {

        "password":
        generate_password_hash("student123")
    }
}


@login_manager.user_loader
def load_user(user_id):

    if user_id in users:

        return User(
            user_id,
            user_id,
            users[user_id]["password"]
        )

    return None


class FineStrategy:

    @staticmethod
    def calculate_fine(days):

        if days <= 7:

            return 0

        return (days - 7) * 5


class Book:

    def __init__(self, book_id, title, author):

        self.id = book_id

        self.title = title

        self.author = author

        self.available = True

        self.borrowed_by = ""

        self.borrow_date = ""

    def to_dict(self):

        return {

            "id": self.id,

            "title": self.title,

            "author": self.author,

            "available": self.available,

            "borrowed_by": self.borrowed_by,

            "borrow_date": self.borrow_date
        }


class Library:

    @staticmethod
    def get_books():

        with open(BOOKS_FILE, "r") as file:

            return json.load(file)

    @staticmethod
    def save_books(books):

        with open(BOOKS_FILE, "w") as file:

            json.dump(
                books,
                file,
                indent=4
            )


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        if username in users and check_password_hash(
            users[username]["password"],
            password
        ):

            user = User(
                username,
                username,
                users[username]["password"]
            )

            login_user(user)

            return redirect(
                url_for("home")
            )

    return render_template(
        "login.html"
    )


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )


@app.route("/")
@login_required
def home():

    books = Library.get_books()

    return render_template(
        "index.html",
        books=books,
        user=current_user.username
    )


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_book():

    if request.method == "POST":

        book_id = int(request.form["id"])

        title = request.form["title"]

        author = request.form["author"]

        new_book = Book(
            book_id,
            title,
            author
        )

        books = Library.get_books()

        books.append(
            new_book.to_dict()
        )

        Library.save_books(books)

        return redirect(
            url_for("home")
        )

    return render_template(
        "add_book.html"
    )


@app.route("/borrow", methods=["GET", "POST"])
@login_required
def borrow_book():

    if request.method == "POST":

        student_name = request.form["student"]

        book_id = int(
            request.form["book_id"]
        )

        books = Library.get_books()

        for book in books:

            if book["id"] == book_id:

                if book["available"]:

                    book["available"] = False

                    book["borrowed_by"] = student_name

                    book["borrow_date"] = str(
                        datetime.now().date()
                    )

        Library.save_books(books)

        return redirect(
            url_for("home")
        )

    return render_template(
        "borrow_book.html"
    )


@app.route("/return", methods=["GET", "POST"])
@login_required
def return_book():

    fine = None

    if request.method == "POST":

        book_id = int(
            request.form["book_id"]
        )

        books = Library.get_books()

        for book in books:

            if book["id"] == book_id:

                if not book["available"]:

                    borrow_date = datetime.strptime(
                        book["borrow_date"],
                        "%Y-%m-%d"
                    )

                    days_used = (
                        datetime.now() - borrow_date
                    ).days

                    fine = FineStrategy.calculate_fine(
                        days_used
                    )

                    book["available"] = True

                    book["borrowed_by"] = ""

                    book["borrow_date"] = ""

        Library.save_books(books)

    return render_template(
        "return_book.html",
        fine=fine
    )


if __name__ == "__main__":

    app.run(debug=True)
