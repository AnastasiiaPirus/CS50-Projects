import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from datetime import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    user_id = session["user_id"]
    portfolio = db.execute(
        "SELECT symbol, name, SUM(shares) FROM users JOIN transactions ON users.id = transactions.user_id WHERE id = ? GROUP BY symbol", user_id)
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)

    cash = (cash[0]["cash"])
    print(portfolio)
    print(cash)

    portfolio_len = len(portfolio)
    symbols = [d['symbol'] for d in portfolio]
    names = [d['name'] for d in portfolio]
    sharesN = [d['SUM(shares)'] for d in portfolio]
    prices = []

    for symbol in symbols:
        info = lookup(symbol)
        price_current = info["price"]
        prices.append(price_current)

    totalsForSum = []
    total = 0
    for num1, num2 in zip(sharesN, prices):
        totalsForSum.append(round(num1 * num2, 2))

    for i in totalsForSum:
        total = total + int(i)

    totalWithCash = usd(total + cash)
    total = usd(total)
    totalsForHTML = []
    for num1, num2 in zip(sharesN, prices):
        totalsForHTML.append(usd(round(num1 * num2, 2)))

    # print(totals)

    # print (symbols)
    # print (prices)

    # return apology("TODO")
    return render_template("index.html", portfolio_len=portfolio_len, symbols=symbols, names=names, sharesN=sharesN, prices=prices, totalsForHTML=totalsForHTML, cash=cash, totalWithCash=totalWithCash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        symbol = request.form.get("symbol")

        if not request.form.get("shares"):
            return apology("must provide shares", 400)

        try:
            shares = float(request.form.get("shares"))
        except:
            return apology("incorrect input", 400)

        if shares.is_integer() != True:
            return apology("must provide valid integer", 400)

        if shares <= 0:
            return apology("shares can't be negative", 400)

        if len(symbol) == 0:
            return apology("symbol doesn't exist", 400)

        if lookup(symbol) == None:
            return apology("symbol doesn't exist", 400)
        info = lookup(symbol)

        name = info["name"]
        symbol1 = info["symbol"]
        price = info["price"]
        priceUSD = usd(price)

        totalPrice = float(round(shares * price, 2))

        user_id = session["user_id"]
        # print (user_id)

        availableCash = db.execute(
            "SELECT cash FROM users WHERE id = ?", user_id)

        availableCash = float(availableCash[0]['cash'])

        if totalPrice > availableCash:
            return apology("that's too much money", 403)

        try:
            db.execute(
                "CREATE TABLE transactions (user_id TEXT,  transaction_type TEXT, shares FLOAT, symbol TEXT , name TEXT, time TEXT, price TEXT);")
        except:
            print("Table already exists")

        newCash = availableCash - totalPrice
        transaction_type = "buy"
        now = datetime.now()
        time = now.strftime("%d/%m/%Y %H:%M:%S")

        db.execute("INSERT INTO transactions (user_id, transaction_type, shares, symbol, name, time, price ) VALUES(?, ?, ?, ?, ?, ?, ?);",
                   user_id, transaction_type, shares, symbol1, name, time, priceUSD)
        db.execute("UPDATE users SET cash = ?  WHERE id = ?;",
                   newCash, user_id)

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    transactions = db.execute(
        "SELECT symbol, shares, price, time FROM users JOIN transactions ON users.id = transactions.user_id WHERE id = ? ;", user_id)
    # cash = db.execute("SELECT cash FROM users WHERE id = ?;", user_id)

    # cash = (cash[0]["cash"])
    # print (portfolio)
    # print (cash)

    transactions_len = len(transactions)
    symbols = [d['symbol'] for d in transactions]
    shares = [d['shares'] for d in transactions]
    prices = [d['price'] for d in transactions]
    times = [d['time'] for d in transactions]

    return render_template("history.html", transactions_len=transactions_len, symbols=symbols,  shares=shares, prices=prices, times=times)


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
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

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
    if request.method == "POST":

        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        symbol = request.form.get("symbol")

        if len(symbol) == 0:
            return apology("symbol doesn't exist", 400)
        if lookup(symbol) == None:
            return apology("symbol doesn't exist", 400)

        info = lookup(symbol)
        name = info["name"]
        symbol1 = info["symbol"]
        price = usd(info["price"])

        return render_template("quoted.html", name=name, symbol=symbol1, price=price)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords doesn't match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) == 1:
            return apology("username already exists", 400)

        username = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))

        db.execute(
            "INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        # Remember which user has logged in

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

    # return apology("TODO")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]

    if request.method == "POST":
        if not request.form.get("shares"):
            return apology("must provide shares", 400)

        try:
            shares = float(request.form.get("shares"))
        except:
            return apology("incorrect input", 400)

        if shares.is_integer() != True:
            return apology("must provide valid integer", 400)

        if shares <= 0:
            return apology("shares can't be negative", 400)

        symbol = request.form.get("symbol")

        if len(symbol) == 0:
            return apology("symbol doesn't exist", 400)

        if lookup(symbol) == None:
            return apology("symbol doesn't exist", 400)
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        info = lookup(symbol)
        name = info["name"]
        symbol1 = info["symbol"]

        availableShares = db.execute(
            "SELECT SUM(shares) FROM users JOIN transactions ON users.id = transactions.user_id WHERE id = ? AND symbol = ?;", user_id, symbol1)

        price = info["price"]
        priceUSD = usd(price)

        totalPrice = float(round(shares * price, 2))

        availableShares = db.execute(
            "SELECT SUM(shares) FROM users JOIN transactions ON users.id = transactions.user_id WHERE id = ? AND symbol = ?;", user_id, symbol1)
        availableShares = float(availableShares[0]['SUM(shares)'])

        if shares > availableShares:
            return apology("not enought shares", 400)
        try:
            db.execute(
                "CREATE TABLE transactions (user_id TEXT,  transaction_type TEXT, shares FLOAT, symbol TEXT , name TEXT, time TEXT, price TEXT);")
        except:
            print("Table already exists")

        shares = shares * (-1)
        transaction_type = "sell"
        now = datetime.now()
        time = now.strftime("%d/%m/%Y %H:%M:%S")

        db.execute("INSERT INTO transactions (user_id, transaction_type, shares, symbol, name, time, price) VALUES(?, ?, ?, ?, ?, ?, ?);",
                   user_id, transaction_type, shares, symbol1, name, time, priceUSD)
        # newtable = db.execute( "SELECT * FROM transactions;")
        # print(newtable)

        availableCash = db.execute(
            "SELECT cash FROM users WHERE id = ?", user_id)

        availableCash = float(availableCash[0]['cash'])
        newCash = availableCash + totalPrice

        db.execute("UPDATE users SET cash = ?  WHERE id = ?;",
                   newCash, user_id)

        # Redirect user to home page
        return redirect("/")

    else:
        share_names = db.execute(
            "SELECT symbol FROM users JOIN transactions ON users.id = transactions.user_id WHERE id = ?;", user_id)
        # foreach ['name'] select to list.
        # convert list to set.

        share_names = set([d['symbol'] for d in share_names])
        print(share_names)
        return render_template("sell.html", share_names=share_names)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":

        if not request.form.get("amount"):
            return apology("must provide amount", 400)
        addedCash = float(request.form.get("amount"))

        user_id = session["user_id"]

        availableCash = db.execute(
            "SELECT cash FROM users WHERE id = ?", user_id)
        availableCash = float(availableCash[0]['cash'])
        newCash = availableCash + addedCash

        db.execute("UPDATE users SET cash = ?  WHERE id = ?;",
                   newCash, user_id)
        return redirect("/")
    else:
        return render_template("add.html")
