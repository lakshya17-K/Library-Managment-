from models import Book


class User:

    def __init__(self, name):
        self.name = name


class Student(User):

    def borrow(self, library, book_id):
        library.borrow_book(self.name, book_id)

    def return_book(self, library, book_id):
        library.return_book(book_id)


class Admin(User):

    def add_book(self, library):

        book_id = int(input("Enter Book ID: "))
        title = input("Enter Book Title: ")
        author = input("Enter Author Name: ")
        genre = input("Enter Genre: ")

        new_book = Book(
            book_id,
            title,
            author,
            genre
        )

        library.add_book(new_book)


class UserFactory:

    @staticmethod
    def create_user(role, name):

        role = role.lower()

        if role == "admin":
            return Admin(name)

        if role == "student":
            return Student(name)

        return None
