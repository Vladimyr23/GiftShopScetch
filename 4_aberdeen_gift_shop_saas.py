"""
SaaS-Grade Aberdeen Gift Shop (Flask)
Features:
- Admin + Staff roles
- Stripe Checkout
- Orders system
- Basic analytics dashboard
- Modern API-style structure (single-file demo)
"""

from flask import Flask, request, redirect, url_for, session, render_template_string, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import stripe
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///saas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_replace_me')
DOMAIN = os.getenv('DOMAIN_URL', 'http://localhost:5000')

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(255))
    role = db.Column(db.String(20), default='admin')  # admin / staff

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    price = db.Column(db.Integer)  # pence
    stock = db.Column(db.Integer, default=0)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    total = db.Column(db.Integer)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------- INIT ----------------

@app.before_first_request
def init():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin'
        ))
        db.session.commit()

# ---------------- UI ----------------

HOME = """
<html>
<head>
<title>SaaS Gift Shop</title>
<style>
body{font-family:Arial;margin:0;background:#f4f6f8}
header{background:#111827;color:white;padding:15px}
.container{max-width:1100px;margin:auto;padding:20px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:15px}
.card{background:white;padding:15px;border-radius:12px;box-shadow:0 6px 18px rgba(0,0,0,0.08)}
.btn{background:#2563eb;color:white;padding:10px;border:none;border-radius:8px;text-decoration:none;display:inline-block}
</style>
</head>
<body>
<header><strong>Aberdeen Gift SaaS</strong> | <a href='/dashboard' style='color:white'>Admin</a></header>
<div class='container'>
<h1>Premium Gift Store</h1>
<div class='grid'>
{% for p in products %}
<div class='card'>
<h3>{{p.name}}</h3>
<p>£{{p.price/100}}</p>
<a class='btn' href='/buy/{{p.id}}'>Buy</a>
</div>
{% endfor %}
</div>
</div>
</body>
</html>
"""

LOGIN = """
<h2>Login</h2>
<form method='post'>
<input name='username' placeholder='username'><br>
<input name='password' type='password'><br>
<button>Login</button>
</form>
"""

DASH = """
<h1>Admin Dashboard</h1>
<p><a href='/analytics'>Analytics</a> | <a href='/logout'>Logout</a></p>

<h2>Add Product</h2>
<form method='post' action='/add'>
<input name='name' placeholder='name'>
<input name='price' placeholder='price in pence'>
<input name='stock' placeholder='stock'>
<button>Add</button>
</form>

<h2>Products</h2>
{% for p in products %}
<p>{{p.name}} - £{{p.price/100}} Stock: {{p.stock}}</p>
{% endfor %}

<h2>Orders</h2>
{% for o in orders %}
<p>#{{o.id}} | {{o.email}} | £{{o.total/100}} | {{o.status}}</p>
{% endfor %}
"""

ANALYTICS = """
<h1>Analytics</h1>
<p>Total Orders: {{orders}}</p>
<p>Total Revenue: £{{revenue/100}}</p>
<p>Products: {{products}}</p>
<a href='/dashboard'>Back</a>
"""

# ---------------- AUTH ----------------

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u = User.query.filter_by(username=request.form['username']).first()
        if u and check_password_hash(u.password, request.form['password']):
            session['user']=u.username
            return redirect('/dashboard')
    return LOGIN

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- STORE ----------------

@app.route('/')
def home():
    return render_template_string(HOME, products=Product.query.all())

@app.route('/buy/<int:id>')
def buy(id):
    product = Product.query.get_or_404(id)

    checkout = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'gbp',
                'product_data': {'name': product.name},
                'unit_amount': product.price,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=DOMAIN + '/success',
        cancel_url=DOMAIN + '/',
    )

    return redirect(checkout.url)

@app.route('/success')
def success():
    return '<h1>Payment Successful 🎉</h1><a href="/">Back</a>'

# ---------------- ADMIN ----------------

@app.route('/dashboard')
def dashboard():
    if session.get('user') != 'admin':
        return redirect('/login')
    return render_template_string(DASH,
        products=Product.query.all(),
        orders=Order.query.all()
    )

@app.route('/add', methods=['POST'])
def add():
    if session.get('user') != 'admin':
        return redirect('/login')

    p = Product(
        name=request.form['name'],
        price=int(request.form['price']),
        stock=int(request.form['stock'])
    )
    db.session.add(p)
    db.session.commit()
    return redirect('/dashboard')

# ---------------- ANALYTICS ----------------

@app.route('/analytics')
def analytics():
    if session.get('user') != 'admin':
        return redirect('/login')

    orders = Order.query.count()
    revenue = sum(o.total for o in Order.query.all())
    products = Product.query.count()

    return render_template_string(ANALYTICS,
        orders=orders,
        revenue=revenue,
        products=products
    )

# ---------------- RUN ----------------

if __name__ == '__main__':
    app.run(debug=True)
