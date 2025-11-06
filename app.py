from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.Product import ProductModel

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key in production
product_model = ProductModel()

# Static user data using dictionary
users = {
    'admin': {
        'username': 'admin',
        'password': '2wsx1qaz',  # In a real app, you should hash the password
        'role': 'admin'
    },
}

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user exists and password is correct
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            flash('Login successful!', 'success')
            return redirect(url_for('read'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('read'))

# Check if user is logged in
def is_logged_in():
    return 'username' in session

# Check if user has admin privileges
def is_admin():
    return 'role' in session and session['role'] == 'admin'

# Update existing routes to implement authentication
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/produk')
def read():
    products = product_model.getAllProduct()
    return render_template('read.html', products=products)

@app.route('/produk/tambah', methods=['GET', 'POST'])
def create():
    if not is_logged_in():
        flash('Please log in to add products', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_data = {
            'nama': request.form['nama'],
            'origin': request.form['origin'],
            'roast': request.form['roast'],
            'harga': request.form['harga'],
            'stok': request.form['stok']
        }
        product_model.setProduct(new_data)
        flash('Product added successfully', 'success')
        return redirect(url_for('read'))
    
    return render_template('create.html')

@app.route('/produk/<int:product_id>/ubah', methods=['GET', 'POST'])
def update(product_id):
    if not is_logged_in():
        flash('Please log in to update products', 'error')
        return redirect(url_for('login'))
    
    product = product_model.getProductById(product_id)
    
    if request.method == 'POST':
        updated_data = {
            'nama': request.form['nama'],
            'origin': request.form['origin'],
            'roast': request.form['roast'],
            'harga': request.form['harga'],
            'stok': request.form['stok']
        }
        product_model.updateProduct(product_id, updated_data)
        flash('Product updated successfully', 'success')
        return redirect(url_for('read'))
    
    if product:
        return render_template('update.html', product=product)
    else:
        return redirect(url_for('read'))
    
if __name__ == '__main__':
    app.run(debug=True)