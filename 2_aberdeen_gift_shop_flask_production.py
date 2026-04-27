import os
from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import stripe

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_replace_me')
DOMAIN = os.getenv('DOMAIN_URL', 'http://localhost:5000')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer, nullable=False)  # pence
    active = db.Column(db.Boolean, default=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    total = db.Column(db.Integer)
    status = db.Column(db.String(50), default='pending')

TEMPLATE = '''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Aberdeen Gift Shop</title><style>body{font-family:Arial;margin:0;background:#f8fafc}header,footer{background:#102A43;color:#fff;padding:16px}.wrap{max-width:1100px;margin:auto;padding:24px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}.card{background:#fff;padding:18px;border-radius:14px;box-shadow:0 8px 18px rgba(0,0,0,.08)}.btn{background:#D4AF37;color:#102A43;padding:10px 14px;border-radius:8px;text-decoration:none;border:none;font-weight:bold;cursor:pointer}</style></head><body><header><strong>Aberdeen Gift Shop</strong></header><div class="wrap"><h1>Premium Gifts with Free Aberdeen Delivery</h1><div class="grid">{% for p in products %}<div class="card"><h3>{{p.name}}</h3><p>£{{'%.2f'|format(p.price/100)}}</p><a class="btn" href="{{url_for('add_to_cart', pid=p.id)}}">Add to Cart</a></div>{% endfor %}</div><h2 style="margin-top:30px">Basket</h2>{% for item in cart_items %}<p>{{item.name}} - £{{'%.2f'|format(item.price/100)}}</p>{% endfor %}<p><strong>Total: £{{'%.2f'|format(total/100)}}</strong></p><form action="{{url_for('create_checkout_session')}}" method="post"><input name="email" placeholder="Email" required><button class="btn" type="submit">Checkout with Stripe</button></form></div><footer>© 2026 Aberdeen Gift Shop</footer></body></html>'''

@app.before_first_request
def setup():
    db.create_all()
    if Product.query.count() == 0:
        db.session.add(Product(name='Luxury Chocolate Hamper', price=2999))
        db.session.add(Product(name='Birthday Surprise Box', price=2499))
        db.session.add(Product(name='Personalised Mug Set', price=1999))
        db.session.commit()

@app.route('/')
def home():
    products = Product.query.filter_by(active=True).all()
    cart = session.get('cart', [])
    cart_items = Product.query.filter(Product.id.in_(cart)).all() if cart else []
    total = sum(i.price for i in cart_items)
    return render_template_string(TEMPLATE, products=products, cart_items=cart_items, total=total)

@app.route('/add/<int:pid>')
def add_to_cart(pid):
    cart = session.get('cart', [])
    cart.append(pid)
    session['cart'] = cart
    return redirect(url_for('home'))

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    cart = session.get('cart', [])
    items = Product.query.filter(Product.id.in_(cart)).all() if cart else []
    if not items:
        return redirect(url_for('home'))
    line_items = []
    total = 0
    for item in items:
        total += item.price
        line_items.append({
            'price_data': {
                'currency': 'gbp',
                'product_data': {'name': item.name},
                'unit_amount': item.price,
            },
            'quantity': 1,
        })
    order = Order(email=request.form['email'], total=total, status='pending')
    db.session.add(order)
    db.session.commit()
    checkout = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=DOMAIN + url_for('success', order_id=order.id),
        cancel_url=DOMAIN + url_for('home')
    )
    return redirect(checkout.url, code=303)

@app.route('/success/<int:order_id>')
def success(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = 'paid'
    db.session.commit()
    session['cart'] = []
    return f'<h1>Thank you!</h1><p>Order #{order.id} confirmed.</p><p><a href="/">Return Home</a></p>'

@app.route('/admin/orders')
def admin_orders():
    orders = Order.query.order_by(Order.id.desc()).all()
    return jsonify([{'id':o.id,'email':o.email,'total':o.total,'status':o.status} for o in orders])

if __name__ == '__main__':
    app.run(debug=True)
