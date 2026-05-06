from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Add a secret key for sessions

# --- DATABASES ---
customers = [
    {'id': '0101', 'name': 'Juan', 'contact': '09223456789', 'address': 'Tubigon'},
    {'id': '0000', 'name': 'Jhonavie', 'contact': '09220987654', 'address': 'Clarin'},
    {'id': '0001', 'name': 'Angel', 'contact': '09123456789', 'address': 'Dagohoy'},
    {'id': '0002', 'name': 'Maria', 'contact': '09123452459', 'address': 'Danao'},
    {'id': '0003', 'name': 'John', 'contact': '09123456789', 'address': 'Mactan'},
    {'id': '0004', 'name': 'Jane', 'contact': '09123456789', 'address': 'Bantayan'},
    {'id': '0005', 'name': 'Heart', 'contact': '09958840258', 'address': 'Nahud'},
]

products = [
    {'id': '1001', 'name': 'Laptop', 'category': 'Electronics', 'price': 45000, 'stock': 'Available', 'status': 'active'},
    {'id': '1010', 'name': 'Television', 'category': 'Electronics', 'price': 32000, 'stock': 'Available', 'status': 'active'},
    {'id': '1234', 'name': 'Refrigerator', 'category': 'Appliances', 'price': 23000, 'stock': 'Available', 'status': 'active'},
    {'id': '1235', 'name': 'Washing Machine', 'category': 'Appliances', 'price': 18000, 'stock': 'Available', 'status': 'active'},
    {'id': '14000', 'name': 'Printer', 'category': 'Electronics', 'price': 5000, 'stock': 'Not Available', 'status': 'active'},
    {'id': '1237', 'name': 'Blender', 'category': 'Appliances', 'price': 2000, 'stock': 'Available', 'status': 'active'},
    {'id': '1238', 'name': 'Toaster', 'category': 'Appliances', 'price': 1500, 'stock': 'Available', 'status': 'active'},
]

sales = [
     {'id': 1, 'customer_id': '0000', 'product': 'Television', 'quantity': 1, 'total': 32000, 'date': '2024-06-01', 'customer': 'Jhonavie', 'payment_type': 'cash'},
     {'id': 2, 'customer_id': '0001', 'product': 'Laptop', 'quantity': 1, 'total': 45000, 'date': '2024-06-02', 'customer': 'Angel', 'payment_type': 'gcash'},
     {'id': 3, 'customer_id': '0002', 'product': 'Refrigerator', 'quantity': 1, 'total': 23000, 'date': '2024-06-03', 'customer': 'Maria', 'payment_type': 'installment'},
]


bills = [
    {'id': 1, 'customer_id': '0000', 'customer': 'Jhonavie', 'amount': 32000, 'date': '2024-06-01', 'status': 'Paid', 'description': 'Television purchase', 'type': 'Full Payment'},
]

activities = []

user_credentials = {
    'admin': {'password': 'admin', 'role': 'admin'},
    'cashier': {'password': 'cashier', 'role': 'cashier'}
}

# --- HELPER FUNCTIONS ---
def log_activity(activity_type, description, user="System"):
    global activities
    activity = {
        'id': len(activities) + 1,
        'type': activity_type,
        'description': description,
        'user': user,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    activities.insert(0, activity)
    if len(activities) > 20:
        activities = activities[:20]

def get_dashboard_metrics():
    total_customers = len(customers)
    total_sales = sum(s['total'] for s in sales)
    total_products = len(products)
    total_products_sold = sum(s['quantity'] for s in sales)
    pending_payments = sum(b['amount'] for b in bills if b['status'] == 'Unpaid')
    total_bills = len(bills)
    paid_bills = len([b for b in bills if b['status'] == 'Paid'])
    unpaid_bills = len([b for b in bills if b['status'] == 'Unpaid'])
    pending_bills = len([b for b in bills if b['status'] == 'Pending'])
    total_revenue = sum(b['amount'] for b in bills if b['status'] == 'Paid')
    return {
        'total_customers': total_customers,
        'total_sales': total_sales,
        'total_products': total_products,
        'total_products_sold': total_products_sold,
        'pending_payments': pending_payments,
        'total_bills': total_bills,
        'paid_bills': paid_bills,
        'unpaid_bills': unpaid_bills,
        'pending_bills': pending_bills,
        'total_revenue': total_revenue,
        'billing_data': bills,
        'activity_log': activities,
        'recent_activities': activities[:10],
        'recent_bills': bills[-5:]
    }

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()

        if username in user_credentials:
            if password == user_credentials[username]['password']:
                log_activity('login', f'User {username} logged in', username)
                role = user_credentials[username]['role']
                session['username'] = username
                session['role'] = role
                if role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif role == 'cashier':
                    return redirect(url_for('cashier_dashboard'))
            else:
                error = "Invalid username or password!"
        else:
            error = "Invalid username or password!"
    return render_template('login.html', error=error)

@app.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html', **get_dashboard_metrics())

@app.route('/cashier')
def cashier_dashboard():
    return render_template('cashier/dashboard.html', **get_dashboard_metrics())

@app.route('/customer_management', methods=['POST', 'GET'])
def customer_management():
    global customers
    error = None
    search_query = ''
    if request.method == 'POST':
        if 'save_customer' in request.form:
            c_id = request.form.get('customerId', '').strip()
            c_name = request.form.get('customerName', '').strip()
            contact = request.form.get('contactNo', '').strip()
            address = request.form.get('address', '').strip()
            if not c_id or not c_name or not contact:
                error = "Customer ID, Name, and Contact are required!"
            else:
                if any(c['id'] == c_id for c in customers):
                    error = "Customer ID already exists!"
                else:
                    customers.append({'id': c_id, 'name': c_name, 'contact': contact, 'address': address, 'status': 'Active'})
                    log_activity('customer', f'Added: {c_name}', 'admin')
                    return redirect(url_for('customer_management'))
        elif 'search_customer' in request.form:
            search_query = request.form.get('searchInput', '').strip().lower()
    
    filtered = [c for c in customers if search_query in c['id'].lower() or search_query in c['name'].lower()] if search_query else customers
    return render_template('admin/customer.html', customers=filtered, error=error, search_query=search_query)

@app.route('/cashier/customer_management', methods=['POST', 'GET'])
def cashier_customer_management():
    global customers
    error = None
    search_query = ''
    if request.method == 'POST':
        if 'save_customer' in request.form:
            c_id = request.form.get('customerId', '').strip()
            c_name = request.form.get('customerName', '').strip()
            contact = request.form.get('contactNo', '').strip()
            address = request.form.get('address', '').strip()
            if not c_id or not c_name or not contact:
                error = "Customer ID, Name, and Contact are required!"
            else:
                if any(c['id'] == c_id for c in customers):
                    error = "Customer ID already exists!"
                else:
                    customers.append({'id': c_id, 'name': c_name, 'contact': contact, 'address': address, 'status': 'Active'})
                    log_activity('customer', f'Added: {c_name}', 'cashier')
                    return redirect(url_for('cashier_customer_management'))
        elif 'search_customer' in request.form:
            search_query = request.form.get('searchInput', '').strip().lower()
    
    filtered = [c for c in customers if search_query in c['id'].lower() or search_query in c['name'].lower()] if search_query else customers
    return render_template('cashier/customer.html', customers=filtered, error=error, search_query=search_query)

@app.route('/delete_customer/<customer_id>')
def delete_customer(customer_id):
    global customers
    customers[:] = [c for c in customers if c['id'] != customer_id]
    log_activity('customer', f'Deleted ID: {customer_id}', 'admin')
    return redirect(url_for('customer_management'))

@app.route('/cashier/delete_customer/<customer_id>')
def cashier_delete_customer(customer_id):
    global customers
    customers[:] = [c for c in customers if c['id'] != customer_id]
    log_activity('customer', f'Deleted ID: {customer_id}', 'cashier')
    return redirect(url_for('cashier_customer_management'))

@app.route('/products', methods=['POST', 'GET'])
def products_management():
    global products
    error = None
    search_query = ''
    if request.method == 'POST':
        if 'save_product' in request.form:
            p_id = request.form.get('productId', '').strip()
            p_name = request.form.get('productName', '').strip()
            cat = request.form.get('category', '').strip()
            prc = request.form.get('price', '').strip()
            stk = request.form.get('stock', '').strip()
            if not p_id or not p_name or not cat or not prc or not stk:
                error = "All fields are required!"
            else:
                try:
                    if any(str(p['id']) == str(p_id) for p in products):
                        error = "Product ID already exists!"
                    else:
                        products.append({'id': p_id, 'name': p_name, 'category': cat, 'price': float(prc), 'stock': stk, 'status': 'active'})
                        log_activity('product', f'Added: {p_name}', 'admin')
                        return redirect(url_for('products_management'))
                except ValueError: 
                    error = "Invalid Price format!"
        elif 'search_product' in request.form:
            search_query = request.form.get('searchInput', '').strip().lower()
            
    filtered = [p for p in products if search_query in str(p['id']) or search_query in p['name'].lower()] if search_query else products
    return render_template('admin/Products.html', products=filtered, error=error, search_query=search_query)

@app.route('/cashier/products', methods=['POST', 'GET'])
def cashier_products_management():
    global products
    error = None
    search_query = ''
    if request.method == 'POST':
        if 'save_product' in request.form:
            p_id = request.form.get('productId', '').strip()
            p_name = request.form.get('productName', '').strip()
            cat = request.form.get('category', '').strip()
            prc = request.form.get('price', '').strip()
            stk = request.form.get('stock', '').strip()
            if not p_id or not p_name or not cat or not prc or not stk:
                error = "All fields are required!"
            else:
                try:
                    if any(str(p['id']) == str(p_id) for p in products):
                        error = "Product ID already exists!"
                    else:
                        products.append({'id': p_id, 'name': p_name, 'category': cat, 'price': float(prc), 'stock': stk, 'status': 'active'})
                        log_activity('product', f'Added: {p_name}', 'cashier')
                        return redirect(url_for('cashier_products_management'))
                except ValueError:
                    error = "Invalid Price format!"
        elif 'search_product' in request.form:
            search_query = request.form.get('searchInput', '').strip().lower()
    filtered = [p for p in products if search_query in str(p['id']) or search_query in p['name'].lower()] if search_query else products
    return render_template('cashier/Products.html', products=filtered, error=error, search_query=search_query)

@app.route('/cashier/edit_product/<product_id>', methods=['GET', 'POST'])
def cashier_edit_product(product_id):
    global products
    product = next((p for p in products if str(p['id']) == str(product_id)), None)
    if request.method == 'POST' and product:
        product['name'] = request.form.get('productName')
        product['price'] = float(request.form.get('price'))
        product['category'] = request.form.get('category')
        product['stock'] = request.form.get('stock')
        return redirect(url_for('cashier_products_management'))
    return render_template('cashier/Products.html', products=products, edit_product=product)

@app.route('/cashier/delete_product/<product_id>')
def cashier_delete_product(product_id):
    global products
    products[:] = [p for p in products if str(p['id']) != str(product_id)]
    return redirect(url_for('cashier_products_management'))

@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    global products
    product = next((p for p in products if str(p['id']) == str(product_id)), None)
    if request.method == 'POST' and product:
        product['name'] = request.form.get('productName')
        product['price'] = float(request.form.get('price'))
        product['category'] = request.form.get('category')
        product['stock'] = request.form.get('stock')
        return redirect(url_for('products_management'))
    return render_template('admin/Products.html', products=products, edit_product=product)

@app.route('/delete_product/<product_id>')
def delete_product(product_id):
    global products
    products[:] = [p for p in products if str(p['id']) != str(product_id)]
    return redirect(url_for('products_management'))

@app.route('/sales', methods=['GET', 'POST'])
def sales_management():
    global sales, bills
    search_query = ''
    if request.method == 'POST':
        if 'add_sale' in request.form:
            prod_name = request.form.get('product')
            cust_name = request.form.get('customer')
            qty = int(request.form.get('quantity'))
            pay_type = request.form.get('payment_type')
            date = request.form.get('date')
            
            matched_prod = next((p for p in products if p['name'] == prod_name), None)
            if matched_prod:
                customer = next((c for c in customers if c['name'] == cust_name), None)
                customer_id = customer['id'] if customer else ''
                total_p = matched_prod['price'] * qty
                new_sale = {'id': len(sales)+1, 'customer_id': customer_id, 'product': prod_name, 'customer': cust_name, 'quantity': qty, 'total': total_p, 'date': date, 'payment_type': pay_type}
                
                if pay_type == 'cash':
                    bills.append({'id': len(bills)+1, 'customer': cust_name, 'amount': total_p, 'date': date, 'status': 'Paid', 'description': f'Full payment {prod_name}', 'type': 'Full Payment'})
                
                sales.append(new_sale)
                return redirect(url_for('sales_management'))
        elif 'search_sale' in request.form:
            search_query = request.form.get('searchInput', '').lower()

    filtered = [s for s in sales if search_query in s['customer'].lower()] if search_query else sales
    return render_template('admin/Sales.html', sales=filtered, products=products, search_query=search_query)

@app.route('/cashier/sales', methods=['GET', 'POST'])
def cashier_sales_management():
    global sales, bills
    search_query = ''
    if request.method == 'POST':
        if 'add_sale' in request.form:
            prod_name = request.form.get('product')
            cust_name = request.form.get('customer')
            qty = int(request.form.get('quantity'))
            pay_type = request.form.get('payment_type')
            date = request.form.get('date')
            
            matched_prod = next((p for p in products if p['name'] == prod_name), None)
            if matched_prod:
                customer = next((c for c in customers if c['name'] == cust_name), None)
                customer_id = customer['id'] if customer else ''
                total_p = matched_prod['price'] * qty
                new_sale = {'id': len(sales)+1, 'customer_id': customer_id, 'product': prod_name, 'customer': cust_name, 'quantity': qty, 'total': total_p, 'date': date, 'payment_type': pay_type}
                
                if pay_type == 'cash':
                    bills.append({'id': len(bills)+1, 'customer': cust_name, 'amount': total_p, 'date': date, 'status': 'Paid', 'description': f'Full payment {prod_name}', 'type': 'Full Payment'})
                
                sales.append(new_sale)
                return redirect(url_for('cashier_sales_management'))
        elif 'search_sale' in request.form:
            search_query = request.form.get('searchInput', '').lower()

    filtered = [s for s in sales if search_query in s['customer'].lower()] if search_query else sales
    return render_template('cashier/Sales.html', sales=filtered, products=products, search_query=search_query)

@app.route('/cashier/payment')
def cashier_payment():
    return render_template('cashier/payment.html')

@app.route('/billing', methods=['GET', 'POST'])
def billing_management():
    if 'username' not in session:
        return redirect(url_for('login'))
    global bills
    error = None
    if request.method == 'POST':
        if 'add_bill' in request.form:
            customer = request.form.get('customer', '').strip()
            amount = request.form.get('amount', '').strip()
            date = request.form.get('date', '').strip()
            status = request.form.get('status', 'Unpaid')
            bill_type = request.form.get('type', 'Manual')
            description = request.form.get('description', '').strip()
            
            if not customer or not amount or not date:
                error = "All fields are required!"
            else:
                try:
                    amount = float(amount)
                    new_id = max([b['id'] for b in bills], default=0) + 1
                    customer_id = ''
                    for c in customers:
                        if c['name'] == customer:
                            customer_id = c['id']
                            break
                    bills.append({
                        'id': new_id,
                        'customer_id': customer_id,
                        'customer': customer,
                        'amount': amount,
                        'date': date,
                        'status': status,
                        'description': description,
                        'type': bill_type
                    })
                    log_activity('billing', f'Bill added for {customer}', session.get('username', 'Unknown'))
                except ValueError:
                    error = "Invalid amount!"
        search_query = request.form.get('searchInput', '').lower()
    else:
        search_query = ''
    
    filtered_bills = [b for b in bills if search_query in b['customer'].lower()] if search_query else bills
    
    metrics = get_dashboard_metrics()
    template = 'cashier/billing.html' if session.get('role') == 'cashier' else 'admin/billing.html'
    return render_template(template, bills=filtered_bills, 
                           total_bills=metrics['total_bills'], paid_bills=metrics['paid_bills'], 
                           unpaid_bills=metrics['unpaid_bills'], total_collected=metrics['total_revenue'],
                           outstanding_amount=sum(b['amount'] for b in bills if b['status'] != 'Paid'),
                           bills_json=json.dumps(filtered_bills), pending_bills=metrics['pending_bills'],
                           search_query=search_query, error=error)

@app.route('/update_bill_status/<int:bill_id>/<status>')
def update_bill_status(bill_id, status):
    for b in bills:
        if b['id'] == bill_id:
            b['status'] = status
    return redirect(url_for('billing_management'))

@app.route('/delete_bill/<int:bill_id>')
def delete_bill(bill_id):
    global bills
    bills = [b for b in bills if b['id'] != bill_id]
    return redirect(url_for('billing_management'))

@app.route('/payment')
def payment():
    return render_template('admin/payment.html')

@app.route('/reports')
def reports():
    search_query = request.args.get('searchInput', '').lower()
    overdue_bills = [b for b in bills if b['status'] != 'Paid']
    if search_query:
        overdue_bills = [b for b in overdue_bills if search_query in b['customer'].lower()]
    total_overdue = len(overdue_bills)
    overdue_amount = sum(b['amount'] for b in overdue_bills)
    reminder_list = [f"Reminder for {b['customer']}: ₱{b['amount']} due on {b.get('due_date', b['date'])}" for b in overdue_bills]
    template = 'cashier/report.html' if session.get('role') == 'cashier' else 'admin/reports.html'
    return render_template(template, overdue_bills=overdue_bills, reminder_list=reminder_list, search_query=search_query, total_overdue=total_overdue, overdue_amount=overdue_amount)

@app.route('/users')
def users():
    user_list = [{'username': k, **v} for k, v in user_credentials.items()]
    return render_template('admin/users.html', users=user_list)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    log_activity('system', 'System Start', 'System')
    app.run(debug=True)