
from flask import Flask, render_template, request, redirect, url_for, session, flash

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management
# Connection String ('Jeny')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


# Table Model (Database Table-er design)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='new')
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # এখানে 'user.id' আপনার User টেবিলের নাম অনুযায়ী হবে
    fullname = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    date_ordered = db.Column(db.DateTime, default=db.func.current_timestamp())

# Table create korar command
with app.app_context():
    db.create_all()
    print("Database Tables Created Successfully!")
    
    from flask import request, render_template, redirect, url_for


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        
        user_name = request.form.get('fullname') 
        user_email = request.form.get('email')
        user_pass = request.form.get('password')

        new_user = User(fullname=user_name, email=user_email, password=user_pass)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # ডাটাবেস থেকে ইউজার খুঁজে বের করা
        user = User.query.filter_by(email=email).first()
        
        # চেক করা ইউজার পাওয়া গেছে কি না এবং পাসওয়ার্ড মিলেছে কি না
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            # যদি না মিলে তবে এরর দেখানো
            return render_template('login.html', error="Invalid email or password")
            
    # GET রিকোয়েস্টের জন্য লগইন পেজ দেখানো
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None) # ইউজার আইডি সেশন থেকে মুছে ফেলা
    session.pop('cart', None)    # চাইলে লগআউট করলে কার্টও খালি করে দিতে পারেন
    return redirect(url_for('home'))

@app.route('/search', methods=['GET'])
def search():
    # সার্চ বারে ইউজার যা লিখেছে তা রিসিভ করা
    search_query = request.args.get('query', '')
    
    if search_query:
        # ডাটাবেসে নামের সাথে মিল থাকা প্রোডাক্ট খোঁজা (case-insensitive)
        results = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()
    else:
        results = []

    # রেজাল্ট নিয়ে নতুন একটি পেজে পাঠানো
    return render_template('search_results.html', products=results, query=search_query)

@app.route('/')
def home():
    # Category onujayi product-gulo alada kora
    new_arrivals = Product.query.filter_by(category='new').all()
    featured_products = Product.query.filter_by(category='featured').all()
    
    return render_template('index.html', new_products=new_arrivals, featured_products=featured_products)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        image = request.form.get('image')
        category = request.form.get('category') # Eta jog korun

        new_product = Product(name=name, price=price, image=image, category=category)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('admin'))
    
    products = Product.query.all()
    orders = Order.query.all()
    return render_template('admin.html', products=products,orders=orders)


@app.route('/delete_product/<int:id>')
def delete_product(id):
    product_to_delete = Product.query.get_or_404(id)
    db.session.delete(product_to_delete)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete_order/<int:id>')
def delete_order(id):
    order_to_delete = Order.query.get_or_404(id)
    db.session.delete(order_to_delete)
    db.session.commit()
    return redirect(url_for('admin'))
    

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    # সেশনে কার্ট না থাকলে একটি খালি লিস্ট তৈরি করবে
    if 'cart' not in session:
        session['cart'] = []
    
    # সেশন থেকে লিস্টটি বের করে নতুন আইডি যোগ করা
    current_cart = list(session['cart'])
    current_cart.append(product_id)
    session['cart'] = current_cart  # আবার সেশনে সেট করা
    
    session.modified = True # সেশন পরিবর্তন হয়েছে তা নিশ্চিত করা
    return redirect(url_for('home')) # এখানে আপনার হোম পেজের ফাংশনের নাম দিন

@app.route('/cart')
def cart():
    # সেশনে কার্ট আছে কি না চেক করা
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', products=[], total=0)

    cart_items = []
    total_price = 0
    
    # সেশনের প্রতিটি আইডির জন্য ডাটাবেস থেকে প্রোডাক্ট খুঁজে বের করা
    for pid in session['cart']:
        product = Product.query.get(pid)
        if product:
            cart_items.append(product)
            total_price += product.price
            
    return render_template('cart.html', products=cart_items, total=total_price)

@app.route('/remove_from_cart/<int:index>')
def remove_from_cart(index):
    if 'cart' in session:
        # সেশনের লিস্টটি কপি করে নিয়ে নির্দিষ্ট প্রোডাক্ট রিমুভ করা
        cart_list = list(session['cart'])
        if index < len(cart_list):
            del cart_list[index]
        session['cart'] = cart_list
        session.modified = True
    return redirect(url_for('cart')) # কার্ট পেজে আবার ফিরে যাওয়া

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # ১. ইউজার লগইন করা আছে কি না চেক করা
    if 'user_id' not in session:
        flash("Please login to place an order")
        return redirect(url_for('login'))

    # ২. কার্ট খালি কি না চেক করা
    if 'cart' not in session or not session['cart']:
        flash("Your cart is empty!")
        return redirect(url_for('home'))

    # ৩. কার্টের মোট দাম হিসেব করা
    # আমরা সরাসরি ডাটাবেস থেকে প্রোডাক্টের দাম নিয়ে আসছি
    cart_items = Product.query.filter(Product.id.in_(session['cart'])).all()
    total = sum(item.price for item in cart_items)

    if request.method == 'POST':
        # ৪. ফরম থেকে ইউজারের দেওয়া তথ্য সংগ্রহ করা
        u_name = request.form.get('name')
        u_address = request.form.get('address')
        u_phone = request.form.get('phone')

        try:
            # ৫. অর্ডারটি ডাটাবেসে সেভ করা
            new_order = Order(
                user_id=session['user_id'],
                fullname=u_name,
                address=u_address,
                phone=u_phone,
                total_price=total,
                status='Pending' # ডিফল্ট স্ট্যাটাস
            )
            
            db.session.add(new_order)
            db.session.commit()

            # ৬. অর্ডার সফল হওয়ার পর কার্ট খালি করে দেওয়া
            session.pop('cart', None)
            session.modified = True
            
            # ৭. একই পেজে সাকসেস মেসেজ দেখানোর জন্য success=True পাঠানো
            return render_template('checkout.html', success=True)
            
        except Exception as e:
            db.session.rollback()
            return f"There was an issue placing your order: {e}"

    # ৮. প্রথমবার পেজ লোড হলে (GET Request) ফরমটি দেখাবে
    return render_template('checkout.html', total=total, success=False)

import os

if __name__ == '__main__':
    # Render সার্ভারের পোর্ট রিড করার জন্য
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)