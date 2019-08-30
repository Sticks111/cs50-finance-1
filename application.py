# lines of code 2-43, 67-70, 126-129, 136-187, 210-212, 298-301, 365-372, were provided by cs50 and not written by me.
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    stocks = db.execute(
        "SELECT symbol, SUM(shares) as tot_shares FROM purchases WHERE user_id = :user_id GROUP BY symbol HAVING tot_shares >= 1", user_id=session["user_id"])

    cash_row = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])

    cash = cash_row[0]["cash"]

    shares = {}

    total_total = float(cash)

    stock_price = {}
    for stock in stocks:
        stock_price[stock["symbol"]] = lookup(stock["symbol"])
        shares[stock["symbol"]] = stock["tot_shares"]

    for stock in stock_price:
        total_total += stock_price[stock]["price"] * shares[stock]

    return render_template("index.html", stocks=stocks, stock_price=stock_price, total_total=total_total, cash=cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # Checks is request received by POST
    if request.method == "POST":

        # Generates dictionary containing stock info with lookup function
        Dictionary = lookup(request.form.get("symbol"))

        # Checks if symbol exists or is valid
        if Dictionary == None:
            return apology("cannot find symbol")

        # Stores number of shares to buy
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("you must input a whole number")

        # Checks if number of shares is a positive integer
        if shares < 1:
            return apology("please enter a positive integer")

        # Stores price of one share
        stock_price = Dictionary["price"]

        # Stores symbol
        symbol = Dictionary["symbol"]

        # Queries cash available
        cash_row = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])

        # Stores cash available in cash variable
        cash = cash_row[0]["cash"]

        # stores total cost of all the shares that user is trying to buy
        total_cost = stock_price * shares

        if total_cost > cash:
            return apology("you cannot afford that number of shares")

        # updates available cash
        new_cash = cash - total_cost
        db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash=new_cash, id=session["user_id"])

        # stores purchase history
        db.execute("INSERT into purchases ('user_id', 'symbol', 'shares', 'price') VALUES (:id, :symbol, :shares, :price)",
                   id=session["user_id"], symbol=symbol, shares=shares, price=stock_price)

        # returns to index
        return redirect(url_for("index"))

    # If request received via GET return the quote page
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    history = db.execute(
        "SELECT symbol, shares, price, date FROM purchases WHERE user_id = :id ORDER BY date DESC", id=session["user_id"])
    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # Checks is request received by POST
    if request.method == "POST":

        # Generates dictionary containing stock info with lookup function
        Dictionary = lookup(request.form.get("symbol"))

        # Checks if symbol exists or is valid
        if Dictionary == None:
            return apology("cannot find symbol")

        # Formats the price into USD
        DPrice = usd(Dictionary["price"])

        # Returns quoted page
        return render_template("quoted.html", Dictionary=Dictionary, DPrice=DPrice)

    # If request received via GET return the quote page
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Stores username, password, and confirmation
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username")

        # Ensure password was submitted
        elif not password:
            return apology("must provide password")

        # Ensure password was confirmed
        elif not confirmation:
            return apology("must confirm password")

        # Ensure passwords match
        elif password != confirmation:
            return apology("passwords must match")

        # Store hashed password
        hash = generate_password_hash(password)

        # Insert newly registeated username and password into database
        result = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=hash)
        if not result:
            return apology("username already exists")

        # Remember which user has logged in
        session["user_id"] = result

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    """Lets user change password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Stores new password and confirmation
        newpassword = request.form.get("newpassword")
        confirmation = request.form.get("confirmation")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])

        # Ensure password was submitted
        if not newpassword:
            return apology("must provide a new password")

        # Ensure password was confirmed
        elif not confirmation:
            return apology("must confirm new password")

        # Ensure new passwords match
        elif newpassword != confirmation:
            return apology("passwords must match")

        # Store hashed password
        hash = generate_password_hash(newpassword)

        # Update password in database
        db.execute("UPDATE users SET hash = :hash WHERE id = :id", hash=hash, id=session["user_id"])

        # returns to index
        return redirect(url_for("index"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("changepassword.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Checks is request received by POST
    if request.method == "POST":

        # Generates dictionary containing stock info with lookup function
        Dictionary = lookup(request.form.get("symbol"))

        # Stores symbol
        symbol = Dictionary["symbol"]

        # Checks if symbol exists or is valid
        if Dictionary == None:
            return apology("cannot find symbol")

        # Stores number of shares to buy
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("you must input a whole number")

        # Checks if number of shares is a positive integer
        if shares < 1:
            return apology("please enter at least one share to sell")

        # Checks if number of shares available in portfolio
        stocks_db = db.execute("SELECT SUM(shares) as tot_shares FROM purchases WHERE user_id = :user_id AND symbol = :symbol",
                               user_id=session["user_id"], symbol=symbol)
        stocks = stocks_db[0]["tot_shares"]
        if shares > stocks:
            return apology("you do not have enough shares to sell")

        # converts shares to negative value
        neg_shares = 0 - shares

        # Queries cash available
        cash_row = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])

        # Stores cash available in cash variable
        cash = cash_row[0]["cash"]

        # stock price
        stock_price = Dictionary["price"]

        # updates available cash
        new_cash = cash + (stock_price * shares)
        db.execute("UPDATE users SET cash = :cash WHERE id = :id", cash=new_cash, id=session["user_id"])

        # stores sell into purchase history
        db.execute("INSERT into purchases ('user_id', 'symbol', 'shares', 'price') VALUES (:id, :symbol, :shares, :price)",
                   id=session["user_id"], symbol=symbol, shares=neg_shares, price=stock_price)

        # returns to index
        return redirect(url_for("index"))

    # If request received via GET return the quote page
    else:
        # Generates list of symbols available for select drop down menu
        avail_stocks = db.execute(
            "SELECT symbol, SUM(shares) as tot_shares FROM purchases WHERE user_id = :user_id GROUP BY symbol HAVING tot_shares >= 1", user_id=session["user_id"])

        return render_template("sell.html", avail_stocks=avail_stocks)


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
