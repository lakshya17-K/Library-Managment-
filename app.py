from flask import Flask, render_template, request, redirect, session, jsonify

from library import Library
from users import Users
from fine import FineStrategy

app = Flask(__name__)
app.secret_key = "library_secret_key"

library = Library()
users = Users()


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.validate(username, password):
            session["user"] = username
            return redirect("/")

        return "❌ Invalid Credentials"

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ---------------- HOME ----------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    return render_template("index.html", books=library.get_books(), user=session["user"])


# ---------------- ADD ----------------
@app.route("/add_book", methods=["POST"])
def add_book():
    title = request.form["title"]
    library.add_book(title)
    return redirect("/")


# ---------------- BORROW ----------------
@app.route("/borrow_book", methods=["POST"])
def borrow_book():
    title = request.form["title"]
    library.borrow_book(title)
    return redirect("/")


# ---------------- RETURN ----------------
@app.route("/return_book", methods=["POST"])
def return_book():
    title = request.form["title"]

    fine = FineStrategy.calculate_fine(title)
    library.return_book(title)

    return redirect("/")


# ---------------- CHATBOT ----------------
def chatbot(msg):
    msg = msg.lower()

    if "add" in msg:
        return "📚 Go to Add Book page"
    elif "borrow" in msg:
        return "📘 Go to Borrow page"
    elif "return" in msg:
        return "🔄 Go to Return page"
    elif "fine" in msg:
        return "💰 Fine depends on delay"
    elif "hello" in msg:
        return "👋 Hello! I am Library AI"
    else:
        return "🤖 Ask: add, borrow, return, fine"


@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json["message"]
    return jsonify({"reply": chatbot(msg)})


# ---------------- RUN (RAILWAY SAFE) ----------------
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
