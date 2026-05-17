from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_login import login_required
from flask_login import logout_user
from flask_login import current_user
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

import sqlite3
import json
import os
from datetime import datetime

app = Flask(__name__)

app.secret_key = "supersecretkey"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

BOOKS_FILE = "books.json"
DATABASE = "database.db"


if not os.path.exists(BOOKS_FILE):

    with open(BOOKS_FILE, "w") as file:

        json.dump([], file)


conn = sqlite3.connect(DATABASE)

cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """
)

conn.commit()
conn.close()


class User(UserMixin):

    def __init__(self, id, username, password):

        self.id = str(id)
        self.username = username
        self.password = password


@login_manager.user_loader
def load_user(user_id):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    if user:

        return User(
            user[0],
            user[1],
            user[2]
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


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]

        password = generate_password_hash(
            request.form["password"]
        )

        conn = sqlite3.connect(DATABASE)

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            flash("Username already exists")

            conn.close()

            return redirect(url_for("register"))

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        conn.commit()

        conn.close()

        flash("Registration successful")

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)

        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):

            logged_user = User(
                user[0],
                user[1],
                user[2]
            )

            login_user(logged_user)

            return redirect(url_for("home"))

        flash("Invalid username or password")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))


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

        return redirect(url_for("home"))

    return render_template("add_book.html")


@app.route("/borrow", methods=["GET", "POST"])
@login_required
def borrow_book():

    if request.method == "POST":

        student_name = request.form["student"]

        book_id = int(request.form["book_id"])

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

        return redirect(url_for("home"))

    return render_template("borrow_book.html")


@app.route("/return", methods=["GET", "POST"])
@login_required
def return_book():

    fine = None

    if request.method == "POST":

        book_id = int(request.form["book_id"])

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

                    fine = FineStrategy.calculate_fine(days_used)

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
