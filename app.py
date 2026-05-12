from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

app = Flask(__name__)

BOOKS_FILE = "books.json"


if not os.path.exists(BOOKS_FILE):
    with open(BOOKS_FILE, "w") as file:
        json.dump([], file)


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
            json.dump(books, file, indent=4)


@app.route("/")
def home():

    books = Library.get_books()

    return render_template(
        "index.html",
        books=books
    )


@app.route("/add", methods=["GET", "POST"])
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

        books.append(new_book.to_dict())

        Library.save_books(books)

        return redirect("/")

    return render_template("add_book.html")


@app.route("/borrow", methods=["GET", "POST"])
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
                    book["borrow_date"] = str(datetime.now().date())

        Library.save_books(books)

        return redirect("/")

    return render_template("borrow_book.html")


@app.route("/return", methods=["GET", "POST"])
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
    app.run(host="0.0.0.0", port=8080)
