from flask import Flask, render_template_string, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'change-this-secret-key'

PRODUCTS = [
    {'id': 1, 'name': 'Luxury Chocolate Hamper', 'price': 29.99},
    {'id': 2, 'name': 'Birthday Surprise Box', 'price': 24.99},
    {'id': 3, 'name': 'Personalised Mug Set', 'price': 19.99},
    {'id': 4, 'name': 'Scottish Treat Basket', 'price': 34.99},
]

TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aberdeen Gift Shop</title>
<style>
body{font-family:Arial,sans-serif;margin:0;background:#f8fafc;color:#111827}header,footer{background:#102A43;color:#fff;padding:16px}main{max-width:1100px;margin:auto;padding:24px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}.card{background:#fff;padding:18px;border-radius:14px;box-shadow:0 8px 18px rgba(0,0,0,.08)}.btn{display:inline-block;background:#D4AF37;color:#102A43;padding:10px 14px;border-radius:8px;text-decoration:none;font-weight:bold}.hero{padding:30px 0}.row{display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap}.input{padding:10px;border:1px solid #cbd5e1;border-radius:8px;width:100%}
</style>
</head>
<body>
<header><div class="row"><strong>Aberdeen Gift Shop</strong><div>Basket: {{ cart_count }} items</div></div></header>
<main>
<section class="hero"><h1>Premium Gifts with Free Aberdeen Delivery</h1><p>Luxury hampers, birthday presents and personalised gifts.</p></section>
<section>
<h2>Products</h2>
<div class="grid">
{% for p in products %}
<div class="card">
<h3>{{ p.name }}</h3>
<p>£{{ '%.2f'|format(p.price) }}</p>
<a class="btn" href="{{ url_for('add_to_cart', product_id=p.id) }}">Add to Cart</a>
</div>
{% endfor %}
</div>
</section>
<section style="margin-top:30px" class="grid">
<div class="card">
<h2>Your Basket</h2>
{% if cart_items %}
{% for item in cart_items %}<p>{{ item.name }} - £{{ '%.2f'|format(item.price) }}</p>{% endfor %}
<p><strong>Total: £{{ '%.2f'|format(total) }}</strong></p>
{% else %}<p>No items in basket.</p>{% endif %}
</div>
<div class="card">
<h2>Checkout</h2>
<form method="post" action="{{ url_for('checkout') }}">
<input class="input" name="name" placeholder="Full Name" required><br><br>
<input class="input" name="email" placeholder="Email" required><br><br>
<input class="input" name="address" placeholder="Address" required><br><br>
<button class="btn" type="submit">Place Order</button>
</form>
</div>
</section>
</main>
<footer>© 2026 Aberdeen Gift Shop</footer>
</body>
</html>
'''

@app.route('/')
def home():
    cart = session.get('cart', [])
    cart_items = [p for p in PRODUCTS for cid in cart if p['id'] == cid]
    total = sum(item['price'] for item in cart_items)
    return render_template_string(TEMPLATE, products=PRODUCTS, cart_items=cart_items, total=total, cart_count=len(cart))

@app.route('/add/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', [])
    cart.append(product_id)
    session['cart'] = cart
    return redirect(url_for('home'))

@app.route('/checkout', methods=['POST'])
def checkout():
    session['cart'] = []
    return '<h1>Thank you for your order!</h1><p>Your gift is being prepared.</p><p><a href="/">Return Home</a></p>'

if __name__ == '__main__':
    app.run(debug=True)
