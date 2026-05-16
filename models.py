class Book:

    def __init__(
        self,
        book_id,
        title,
        author,
        genre
    ):

        self.id = book_id
        self.title = title
        self.author = author
        self.genre = genre

        self.available = True
        self.borrowed_by = ""
        self.borrow_date = ""

    def to_dict(self):

        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "available": self.available,
            "borrowed_by": self.borrowed_by,
            "borrow_date": self.borrow_date
        }
