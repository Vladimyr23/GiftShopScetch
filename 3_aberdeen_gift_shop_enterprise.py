from flask import Flask, request, redirect, url_for, session, render_template_string, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY','change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL','sqlite:///enterprise.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(80), unique=True, nullable=False)
    password=db.Column(db.String(255), nullable=False)
    is_admin=db.Column(db.Boolean, default=False)

class Product(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(120), nullable=False)
    price=db.Column(db.Float, nullable=False)
    image=db.Column(db.String(255))
    stock=db.Column(db.Integer, default=0)

@app.before_first_request
def init_db():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password=generate_password_hash('admin123'), is_admin=True))
        db.session.commit()

HOME='''<html><body><h1>Aberdeen Gift Shop Enterprise</h1><p><a href="/login">Admin Login</a> | <a href="/admin">Dashboard</a></p>{% for p in products %}<div><h3>{{p.name}}</h3><p>£{{p.price}}</p>{% if p.image %}<img src="/uploads/{{p.image}}" width="120">{% endif %}</div>{% endfor %}</body></html>'''
LOGIN='''<html><body><h1>Login</h1><form method="post"><input name="username" placeholder="Username"><input name="password" type="password" placeholder="Password"><button>Login</button></form></body></html>'''
ADMIN='''<html><body><h1>Admin Dashboard</h1><p><a href="/logout">Logout</a></p><h2>Add Product</h2><form method="post" enctype="multipart/form-data"><input name="name" placeholder="Name"><input name="price" placeholder="Price"><input name="stock" placeholder="Stock"><input type="file" name="image"><button>Add</button></form><h2>Products</h2>{% for p in products %}<div><strong>{{p.name}}</strong> £{{p.price}} Stock: {{p.stock}} <a href="/delete/{{p.id}}">Delete</a></div>{% endfor %}</body></html>'''

@app.route('/')
def home():
    return render_template_string(HOME, products=Product.query.all())

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=User.query.filter_by(username=request.form['username']).first()
        if u and check_password_hash(u.password, request.form['password']):
            session['user']=u.username
            return redirect('/admin')
    return render_template_string(LOGIN)

@app.route('/logout')
def logout():
    session.clear(); return redirect('/')

@app.route('/admin', methods=['GET','POST'])
def admin():
    if session.get('user')!='admin': return redirect('/login')
    if request.method=='POST':
        file=request.files['image']
        filename=''
        if file and file.filename:
            filename=secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        p=Product(name=request.form['name'], price=float(request.form['price']), stock=int(request.form['stock']), image=filename)
        db.session.add(p); db.session.commit()
        return redirect('/admin')
    return render_template_string(ADMIN, products=Product.query.all())

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('user')!='admin': return redirect('/login')
    p=Product.query.get_or_404(id)
    db.session.delete(p); db.session.commit(); return redirect('/admin')

@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__=='__main__':
    app.run(debug=True)
