import json
import os
from datetime import datetime
from fine import FineStrategy


class Library:
    __instance = None

    @staticmethod
    def get_instance():
        if Library.__instance is None:
            Library()
        return Library.__instance

    def __init__(self):

        if Library.__instance is not None:
            raise Exception("Only one library object allowed!")

        Library.__instance = self

        self.books_file = "books.json"
        self.users_file = "users.json"

        self.setup_files()

    def setup_files(self):

        if not os.path.exists(self.books_file):
            with open(self.books_file, "w") as file:
                json.dump([], file)

        if not os.path.exists(self.users_file):
            with open(self.users_file, "w") as file:
                json.dump([], file)

    def get_books(self):

        with open(self.books_file, "r") as file:
            return json.load(file)

    def save_books(self, books):

        with open(self.books_file, "w") as file:
            json.dump(books, file, indent=4)

    def add_book(self, book):

        books = self.get_books()

        books.append(book.to_dict())

        self.save_books(books)

        print("\nBook added successfully!")

    def view_books(self):

        books = self.get_books()

        if not books:
            print("\nNo books available.")
            return

        for book in books:

            status = (
                "Available"
                if book["available"]
                else "Borrowed"
            )

            print(f"""
Book ID : {book['id']}
Title   : {book['title']}
Author  : {book['author']}
Genre   : {book['genre']}
Status  : {status}
""")

    def search_book(self, keyword):

        books = self.get_books()

        found = False

        for book in books:

            if (
                keyword.lower() in book["title"].lower()
                or keyword.lower() in book["author"].lower()
                or keyword.lower() in book["genre"].lower()
            ):

                found = True

                print(f"""
Book Found
-----------
ID      : {book['id']}
Title   : {book['title']}
Author  : {book['author']}
Genre   : {book['genre']}
""")

        if not found:
            print("\nBook not found.")

    def borrow_book(self, student_name, book_id):

        books = self.get_books()

        for book in books:

            if book["id"] == book_id:

                if not book["available"]:
                    print("\nBook already borrowed.")
                    return

                book["available"] = False
                book["borrowed_by"] = student_name
                book["borrow_date"] = str(datetime.now().date())

                self.save_books(books)

                print("\nBook borrowed successfully!")

                # Show recommendations
                self.recommend_books(book["genre"], book["title"])

                return

        print("\nInvalid Book ID.")

    def return_book(self, book_id):

        books = self.get_books()

        for book in books:

            if book["id"] == book_id:

                if book["available"]:
                    print("\nBook already available.")
                    return

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

                self.save_books(books)

                print(f"""
Book returned successfully!

Days Used : {days_used}
Fine      : ₹{fine}
""")
                return

        print("\nInvalid Book ID.")

    def recommend_books(self, genre, current_title):

        books = self.get_books()

        recommendations = []

        for book in books:

            if (
                book["genre"].lower() == genre.lower()
                and book["title"] != current_title
            ):

                recommendations.append(book)

        if recommendations:

            print("\nRecommended Books")
            print("-------------------")

            for book in recommendations:

                print(f"""
Title  : {book['title']}
Author : {book['author']}
Genre  : {book['genre']}
""")

        else:
            print("\nNo recommendations available.")
