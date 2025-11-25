from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.Product import ProductModel
from models.Order import OrderModel
from models.UserModel import UserModel

app = Flask(__name__)
app.secret_key = 'tiga_roda_kopi_secret'
product_model = ProductModel()
order_model = OrderModel()
user_model = UserModel()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Cari pengguna di database
        user = user_model.find_by_username(username)
        
        # Verifikasi pengguna dan password
        if user and user['password'] == password:
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Authentication helper functions
def is_logged_in():
    return 'username' in session

def is_admin():
    return 'role' in session and session['role'] == 'admin'

def is_user():
    return 'role' in session and session['role'] == 'user'

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

@app.route('/produk/<int:product_id>/hapus', methods=['POST'])
def delete(product_id):
    if not is_logged_in() or session['role'] != 'admin':
        flash('Please log in as an admin to delete products', 'error')
        return redirect(url_for('login'))
    
    product = product_model.getProductById(product_id)
    if product:
        product_model.deleteProduct(product_id)
        flash('Product deleted successfully', 'success')
    else:
        flash('Product not found', 'error')
    return redirect(url_for('read'))

# Shop and cart routes
@app.route('/shop')
def shop():
    products = product_model.getAllProduct()
    return render_template('shop.html', products=products)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not is_logged_in() or session['role'] != 'user':
        flash('Please log in as a user to add items to cart', 'error')
        return redirect(url_for('login'))
    
    # Initialize cart in session if not exists
    if 'cart' not in session:
        session['cart'] = []
    
    # Get form data
    quantity = int(request.form.get('quantity', 1))
    
    # Get the product
    product = product_model.getProductById(product_id)
    
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('shop'))
    
    if quantity > product['stok']:
        flash(f'Stock only available: {product["stok"]} kg', 'error')
        return redirect(url_for('shop'))
    
    # Check if product is already in cart
    cart = session['cart']
    product_exists = False
    
    for item in cart:
        if item['id'] == product_id:
            # Update quantity if adding more would not exceed stock
            if item['quantity'] + quantity <= product['stok']:
                item['quantity'] += quantity
            else:
                flash(f'Cannot add more than {product["stok"]} kg of {product["nama"]}', 'error')
            product_exists = True
            break
    
    # If product not in cart, add it
    if not product_exists:
        cart.append({
            'id': product_id,
            'name': product['nama'],
            'origin': product['origin'],
            'roast': product['roast'],
            'price': product['harga'],
            'quantity': quantity
        })
    
    session['cart'] = cart
    flash(f'{product["nama"]} ditambahkan ke keranjang!', 'success')
    return redirect(url_for('shop'))

@app.route('/cart')
def cart():
    if not is_logged_in() or session['role'] != 'user':
        flash('Please log in as a user to view cart', 'error')
        return redirect(url_for('login'))
    
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/cart/remove/<int:product_id>')
def remove_from_cart(product_id):
    if not is_logged_in() or session['role'] != 'user':
        flash('Please log in as a user to modify cart', 'error')
        return redirect(url_for('login'))
    
    cart = session.get('cart', [])
    session['cart'] = [item for item in cart if item['id'] != product_id]
    flash('Item removed from cart', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not is_logged_in() or session['role'] != 'user':
        flash('Please log in as a user to checkout', 'error')
        return redirect(url_for('login'))
    
    cart_items = session.get('cart', [])
    
    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('shop'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Validate form data
        if not name or not phone or not address:
            flash('Please fill in all delivery information', 'error')
            total = sum(item['price'] * item['quantity'] for item in cart_items)
            return render_template('checkout.html', cart_items=cart_items, total=total)
        
        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in cart_items)
        
        # Process the purchase
        for item in cart_items:
            product = product_model.getProductById(item['id'])
            if product:
                # Update stock
                new_stock = product['stok'] - item['quantity']
                if new_stock < 0:
                    flash(f'Stock tidak mencukupi untuk {product["nama"]}', 'error')
                    total = sum(item['price'] * item['quantity'] for item in cart_items)
                    return render_template('checkout.html', cart_items=cart_items, total=total)
                    
                updated_data = {
                    'nama': product['nama'],
                    'origin': product['origin'],
                    'roast': product['roast'],
                    'harga': product['harga'],
                    'stok': new_stock
                }
                product_model.updateProduct(item['id'], updated_data)
        
        # Create order record
        order = order_model.create_order(
            user_name=name,
            phone=phone,
            address=address,
            items=cart_items,
            total_amount=total
        )
        
        # Clear the cart
        session['cart'] = []
        flash(f'Pembelian berhasil! Terima kasi telah berbelanja. Pesanan #{order["id"]} akan segera diproses.', 'success')
        return redirect(url_for('shop'))
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

# Order management routes for admin
@app.route('/orders')
def orders():
    if not is_logged_in() or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    orders = order_model.get_all_orders()
    return render_template('orders.html', orders=orders)

@app.route('/order/<int:order_id>/status/<string:status>')
def update_order_status(order_id, status):
    if not is_logged_in() or session['role'] != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redisrect(url_for('login'))
    
    # Valid status options
    valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    if status not in valid_statuses:
        flash('Invalid status', 'error')
        return redirect(url_for('orders'))
    
    order = order_model.update_order_status(order_id, status)
    if order:
        flash(f'Status pesanan #{order_id} berhasil diubah menjadi {status}', 'success')
    else:
        flash('Order not found', 'error')
    
    return redirect(url_for('orders'))

if __name__ == '__main__':
    app.run(debug=True)