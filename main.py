from library import Library
from users import UserFactory


def main():

    library = Library.get_instance()

    while True:

        print("""
======= SMART LIBRARY SYSTEM =======

1. Admin
2. Student
3. View Books
4. Search Book
5. Exit
""")

        choice = input("Enter choice: ")

        if choice == "1":

            admin_name = input("Enter admin name: ")

            admin = UserFactory.create_user(
                "admin",
                admin_name
            )

            while True:

                print("""
------ ADMIN MENU ------

1. Add Book
2. View Books
3. Back
""")

                admin_choice = input("Enter choice: ")

                if admin_choice == "1":
                    admin.add_book(library)

                elif admin_choice == "2":
                    library.view_books()

                elif admin_choice == "3":
                    break

                else:
                    print("\nInvalid choice.")

        elif choice == "2":

            student_name = input("Enter student name: ")

            student = UserFactory.create_user(
                "student",
                student_name
            )

            while True:

                print("""
------ STUDENT MENU ------

1. Borrow Book
2. Return Book
3. View Books
4. Back
""")

                student_choice = input("Enter choice: ")

                if student_choice == "1":

                    book_id = int(input("Enter Book ID: "))

                    student.borrow(
                        library,
                        book_id
                    )

                elif student_choice == "2":

                    book_id = int(input("Enter Book ID: "))

                    student.return_book(
                        library,
                        book_id
                    )

                elif student_choice == "3":
                    library.view_books()

                elif student_choice == "4":
                    break

                else:
                    print("\nInvalid choice.")

        elif choice == "3":
            library.view_books()

        elif choice == "4":

            title = input("Enter Book Title: ")

            library.search_book(title)

        elif choice == "5":

            print("\nThank you for using Smart Library System!")
            break

        else:
            print("\nInvalid choice.")


if __name__ == "__main__":
    main()
