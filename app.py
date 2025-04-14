from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Custom filter
quantity=1
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///ecommerce.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    items=db.execute("select * from warehouse")
    user=""
    wishlist=""
    cart=""
    if session:
        items=db.execute("select * from warehouse")
        user = db.execute("select username from users where id = ?",session["user_id"])[0]
        cart = db.execute("select item_name,sum(item_quantity) as total from cart where user_id = ? group by item_id",session["user_id"])
        wishlist = db.execute("select item_name,sum(item_quantity) as total from wishlist where user_id = ? group by item_id",session["user_id"])
    ctotal=0
    wtotal=0
    for i in cart:
        ctotal+=i["total"]
    for i in wishlist:
        wtotal+=i["total"]
    return render_template("index.html",items=items,user=user,ctotal=ctotal,wtotal=wtotal)
@app.route("/search", methods=["GET", "POST"])
def search():
    a=request.form.get("search")
    pattern = f"%{a}%"
    items=db.execute("select * from warehouse where name like ? ",pattern)
    user = db.execute("select username from users where id = ?",session["user_id"])[0]
    cart = db.execute("select item_name,sum(item_quantity) as total from cart where user_id = ? group by item_id",session["user_id"])
    wishlist = db.execute("select item_name,sum(item_quantity) as total from wishlist where user_id = ? group by item_id",session["user_id"])
    ctotal=0
    wtotal=0
    for i in cart:
        ctotal+=i["total"]
    for i in wishlist:
        wtotal+=i["total"]

    return render_template("index.html",items=items,user=user,ctotal=ctotal,wtotal=wtotal)

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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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

@app.route("/product")
def product():
    items=db.execute("select * from warehouse")
    user=""
    wishlist=""
    cart=""
    if session:
        user = db.execute("select username from users where id = ?",session["user_id"])[0]
        cart = db.execute("select item_name,sum(item_quantity) as total from cart where user_id = ? group by item_id",session["user_id"])
        wishlist = db.execute("select item_name,sum(item_quantity) as total from wishlist where user_id = ? group by item_id",session["user_id"])
    ctotal=0
    wtotal=0
    for i in cart:
        ctotal+=i["total"]
    for i in wishlist:
        wtotal+=i["total"]
    n=request.args.get("name")

    product = db.execute("select * from warehouse where name = ?",n)[0]
    return render_template("product.html",cart=cart,user=user,wishlist=wishlist,ctotal=ctotal,wtotal=wtotal,n=n,product=product)


@app.route("/cart")

def mycart():

    user = db.execute("select username from users where id = ?",session["user_id"])[0]
    cart = db.execute("SELECT c.item_name , w.img_url, c.item_price, SUM(c.item_quantity) AS total,SUM(c.item_price * c.item_quantity) AS total_price FROM cart c JOIN warehouse w ON c.item_name = w.name WHERE c.user_id = ? GROUP BY c.item_id, c.item_name, c.item_price, w.img_url",session["user_id"])
    wishlist = db.execute("select item_name,sum(item_quantity) as total from wishlist where user_id = ? group by item_id",session["user_id"])
    ctotal=0
    wtotal=0
    for i in cart:
        ctotal+=i["total"]
    for i in wishlist:
        wtotal+=i["total"]

    return render_template("cart.html",cart=cart,user=user,wishlist=wishlist,ctotal=ctotal,wtotal=wtotal)



@app.route("/addcart", methods=["GET", "POST"])

def addcart():
    if request.method == "POST":
        if not session:
            return redirect("/register")
        product_name = request.form.get("product_name")

        # Check if the product exists in the warehouse
        product = db.execute("SELECT id, selling_price, quantity FROM warehouse WHERE name = ?", product_name)
        if not product:
            return redirect("/")

        product_id = product[0]["id"]
        product_price = product[0]["selling_price"]
        warehouse_quantity = product[0]["quantity"]

        # Check if the product is already in the cart for the current user
        cart_item = db.execute("SELECT item_quantity FROM cart WHERE user_id = ? AND item_name = ?", session["user_id"], product_name)

        if cart_item:
            current_cart_quantity = cart_item[0]["item_quantity"]
            # Check if the total quantity after adding would exceed the warehouse quantity
            if current_cart_quantity + 1 > warehouse_quantity:
                return redirect("/")

            # If the item is already in the cart and the new quantity is within limits, update the quantity
            db.execute("UPDATE cart SET item_quantity = item_quantity + 1 WHERE user_id = ? AND item_name = ?", session["user_id"], product_name)
        else:
            # If the item is not in the cart, check if there's enough stock to add it
            if 1 > warehouse_quantity:
                return redirect("/")

            # Insert a new row in the cart with the initial quantity
            db.execute(
                "INSERT INTO cart (user_id, item_name, item_id, item_quantity, item_price) VALUES (?, ?, ?, ?, ?)",
                session["user_id"], product_name, product_id, 1, product_price
            )

        return redirect("/")

    return redirect("/cart")


@app.route("/addcart1", methods=["GET", "POST"])

def addcart1():
    if request.method == "POST":
        if not session:
            return redirect("/register")
        product_name = request.form.get("product_name")

        # Check if the product exists in the warehouse
        product = db.execute("SELECT id, selling_price, quantity FROM warehouse WHERE name = ?", product_name)
        if not product:
            return redirect("/")

        product_id = product[0]["id"]
        product_price = product[0]["selling_price"]
        warehouse_quantity = product[0]["quantity"]

        # Check if the product is already in the cart for the current user
        cart_item = db.execute("SELECT item_quantity FROM cart WHERE user_id = ? AND item_name = ?", session["user_id"], product_name)

        if cart_item:
            current_cart_quantity = cart_item[0]["item_quantity"]
            # Check if the total quantity after adding would exceed the warehouse quantity
            if current_cart_quantity + 1 > warehouse_quantity:
                return redirect("/")

            # If the item is already in the cart and the new quantity is within limits, update the quantity
            db.execute("UPDATE cart SET item_quantity = item_quantity + 1 WHERE user_id = ? AND item_name = ?", session["user_id"], product_name)
        else:
            # If the item is not in the cart, check if there's enough stock to add it
            if 1 > warehouse_quantity:
                return redirect("/")

            # Insert a new row in the cart with the initial quantity
            db.execute(
                "INSERT INTO cart (user_id, item_name, item_id, item_quantity, item_price) VALUES (?, ?, ?, ?, ?)",
                session["user_id"], product_name, product_id, 1, product_price
            )

        return redirect("/")

    return redirect("/cart")

@app.route("/removeitem",methods=["POST","GET"])
def rmitem():
    if request.method == "POST":
        name=request.form.get("remove")
        db.execute("delete from cart where item_name=? and user_id = ?",name,session["user_id"])
        return redirect("/cart")

    return redirect("/")

@app.route("/checkout",methods=["GET","POST"])
def check():
    if request.method == "POST":
        user = db.execute("select username from users where id = ?",session["user_id"])[0]
        cart = db.execute("select item_name,sum(item_quantity) as total,item_price from cart where user_id = ? group by item_id",session["user_id"])
        wishlist = db.execute("select item_name,sum(item_quantity) as total from wishlist where user_id = ? group by item_id",session["user_id"])
        ctotal=0
        wtotal=0
        for i in cart:
            ctotal+=i["total"]
        for i in wishlist:
            wtotal+=i["total"]
        ttotal = 0
        for i in cart:
            ttotal+=i["total"]*i["item_price"]
        return render_template("checkout.html",user=user,ctotal=ctotal,wtotal=wtotal,ttotal=ttotal)
    return redirect("/")

@app.route("/cod")
def cod():
    t=db.execute("select item_name,item_quantity from cart where user_id=?",session["user_id"])
    db.execute("delete from cart where user_id = ?",session["user_id"])
    for i in t:
        db.execute("update warehouse set quantity = quantity - ? where name=?",i["item_quantity"],i["item_name"])
    flash("You have Successfully Placed Order (COD)")
    return redirect("/")

@app.route("/onlinepay")
def online():
    t=db.execute("select item_name,item_quantity from cart where user_id=?",session["user_id"])
    db.execute("delete from cart where user_id = ?",session["user_id"])
    for i in t:
        db.execute("update warehouse set quantity = quantity - ? where name=?",i["item_quantity"],i["item_name"])
    flash("You have Successfully Placed Order (Pay online)")
    return redirect("/")



@app.route("/updatequantity", methods=["POST"])
def update_quantity():
    item_name = request.form.get("item_name")
    action = request.form.get("action")

    # Get current quantity and warehouse quantity
    cart_item = db.execute("SELECT item_quantity FROM cart WHERE user_id = ? AND item_name = ?", session["user_id"], item_name)
    warehouse_item = db.execute("SELECT quantity FROM warehouse WHERE name = ?", item_name)

    if not cart_item or not warehouse_item:
        return redirect("/cart")

    current_quantity = cart_item[0]["item_quantity"]
    warehouse_quantity = warehouse_item[0]["quantity"]

    if action == "increase" and current_quantity < warehouse_quantity:
        new_quantity = current_quantity + 1
    elif action == "decrease" and current_quantity > 1:
        new_quantity = current_quantity - 1
    else:
        new_quantity = current_quantity

    db.execute("UPDATE cart SET item_quantity = ? WHERE user_id = ? AND item_name = ?", new_quantity, session["user_id"], item_name)
    return redirect("/cart")

@app.route("/add_to_wishlist", methods=["POST"])

def add_to_wishlist():
    if request.method == "POST":
        if not session:
            return redirect("/register")
        product_name = request.form.get("product_name")

        # Check if the product exists in the warehouse
        product = db.execute("SELECT id, selling_price FROM warehouse WHERE name = ?", product_name)
        if not product:
            return redirect("/")

        product_id = product[0]["id"]
        product_price = product[0]["selling_price"]

        # Check if the product is already in the cart for the current user
        wish_item = db.execute("SELECT item_quantity FROM wishlist WHERE user_id = ? AND item_name = ?", session["user_id"], product_name)

        if wish_item:
            # If the item is already in the cart, update the quantity
            db.execute("UPDATE wishlist SET item_quantity = item_quantity + 1 WHERE user_id = ? AND item_name = ?", session["user_id"], product_name)
        else:
            # If the item is not in the cart, insert a new row
            db.execute("INSERT INTO wishlist (user_id, item_name, item_id, item_quantity, item_price) VALUES (?, ?, ?, ?, ?)",session["user_id"], product_name, product_id, 1, product_price)

        return redirect("/")

    return render_template("/wishlist.html",)


@app.route("/move_to_cart", methods=["POST"])
@login_required
def move_to_cart():
    if request.method == "POST":
        product_name = request.form.get("product_name")

        # Check if the product exists in the warehouse
        product = db.execute("SELECT id, selling_price FROM warehouse WHERE name = ?", product_name)
        if not product:
            return redirect("/")

        product_id = product[0]["id"]
        product_price = product[0]["selling_price"]

        wish_item = db.execute("SELECT item_quantity FROM wishlist WHERE user_id = ? AND item_name = ?", session["user_id"], product_name)
        if wish_item:
            db.execute("INSERT INTO cart (user_id, item_name, item_id, item_quantity, item_price) VALUES (?, ?, ?, ?, ?)",session["user_id"], product_name, product_id, 1, product_price)
            db.execute("delete from wishlist where item_name=? and user_id = ?",product_name,session["user_id"])
        else:
            flash("Item not found in wishlist.", "danger")
        items=db.execute("select * from warehouse")
        user = db.execute("select username from users where id = ?",session["user_id"])[0]
        cart = db.execute("select item_name,sum(item_quantity) as total from cart where user_id = ? group by item_id",session["user_id"])
        wishlist = db.execute("select item_name,sum(item_quantity) as total from wishlist where user_id = ? group by item_id",session["user_id"])
        ctotal=0
        wtotal=0
        for i in cart:
            ctotal+=i["total"]
        for i in wishlist:
            wtotal+=i["total"]

    return render_template("wishlist.html",items=items,user=user,ctotal=ctotal,wtotal=wtotal)

@app.route("/remove_from_wishlist",methods=["POST","GET"])
@login_required
def remove_from_wishlist():
    if request.method == "POST":
        name=request.form.get("remove_from_wishlist")
        db.execute("delete from wishlist where item_name=? and user_id = ?",name,session["user_id"])
        return redirect("/wishlist")

    return redirect("/")


@app.route("/wishlist")
@login_required
def wishlist():
    user_id = session["user_id"]

    # Fetch user information
    user = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]

    # Fetch cart items with image URLs
    cart = db.execute("SELECT c.item_name, w.img_url, c.item_price, SUM(c.item_quantity) AS total_quantity,SUM(c.item_price * c.item_quantity) AS total_price FROM cart c JOIN warehouse w ON c.item_name = w.name WHERE c.user_id = ? GROUP BY c.item_id, c.item_name, c.item_price, w.img_url", user_id)

    # Fetch wishlist items with image URLs
    wishlist = db.execute("SELECT wl.item_name, w.img_url, wl.item_price, COUNT(wl.item_name) AS total_quantity FROM wishlist wl JOIN warehouse w ON wl.item_name = w.name WHERE wl.user_id = ? GROUP BY wl.item_id, wl.item_name, wl.item_price, w.img_url", user_id)
    # Calculate total price for cart items


    # Calculate total quantity for wishlist items


    cart1 = db.execute("select item_name,sum(item_quantity) as total from cart where user_id = ? group by item_id",session["user_id"])
    wishlist1 = db.execute("select item_name,sum(item_quantity) as total from wishlist where user_id = ? group by item_id",session["user_id"])
    ctotal=0
    wtotal=0
    for i in cart1:
        ctotal+=i["total"]
    for i in wishlist1:
        wtotal+=i["total"]

    return render_template("wishlist.html", cart=cart, user=user, wishlist=wishlist, ctotal=ctotal, wtotal=wtotal)

@app.route("/profile")
@login_required
def profile():

        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        user = db.execute("select username from users where id = ?",session["user_id"])[0]
        cart = db.execute("select item_name,sum(item_quantity) as total,item_price from cart where user_id = ? group by item_id",session["user_id"])
        wishlist = db.execute("select item_name,sum(item_quantity) as total from wishlist where user_id = ? group by item_id",session["user_id"])
        ctotal=0
        wtotal=0
        for i in cart:
            ctotal+=i["total"]
        for i in wishlist:
            wtotal+=i["total"]
        ttotal = 0
        for i in cart:
            ttotal+=i["total"]*i["item_price"]
        return render_template("profile.html",user=user,ctotal=ctotal,wtotal=wtotal,ttotal=ttotal,rows=rows[0])

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    session.clear()
    username = request.form.get("username")
    email = request.form.get("email")
    tel = request.form.get("tel")
    address = request.form.get("address")
    password = request.form.get("password")
    verify = request.form.get("confirmation")
    if request.method == "POST":
        if not username:
            return apology("Please provide Username", 400)

        elif not password:
            return apology("Please provide Password", 400)

        elif not email:
            return apology("Please provide Email", 400)

        elif not tel:
            return apology("Please provide Phone No", 400)

        elif not address:
            return apology("Please provide Address", 400)

        elif not verify:
            return apology("Password must be verified", 400)

        elif password != verify:
            return apology("Passwords do not match", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 0:
            return apology("username already exists", 400)

        db.execute("INSERT INTO users (username,hash,email,phone_number,address) VALUES(?,?,?,?,?)",
                   username, generate_password_hash(password),email,tel,address)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        session["user_id"] = rows[0]["id"]

        return redirect("/")
    else:
        return render_template("register.html")
