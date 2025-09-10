"""
AccountPro - Professional Account Management System
Built with Flask - Demonstrating Modern Web Development Practices

Features:
- Complete CRUD operations for accounts
- RESTful API design
- Input validation and error handling
- Mobile-responsive design
- Professional application architecture
"""

from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from datetime import datetime
import re
import os
import json

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# In-memory database for demo (replace with actual database in production)
accounts = [
    {
        'id': 1,
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'account_type': 'premium',
        'department': 'Sales',
        'status': 'active',
        'created_date': '2024-01-15',
        'balance': 15750.00
    },
    {
        'id': 2,
        'first_name': 'Sarah',
        'last_name': 'Johnson',
        'email': 'sarah.j@example.com',
        'account_type': 'standard',
        'department': 'Marketing',
        'status': 'active',
        'created_date': '2024-02-20',
        'balance': 8250.00
    },
    {
        'id': 3,
        'first_name': 'Mike',
        'last_name': 'Chen',
        'email': 'mike.chen@example.com',
        'account_type': 'basic',
        'department': 'Support',
        'status': 'inactive',
        'created_date': '2024-03-10',
        'balance': 2100.00
    }
]

# Global counter for unique IDs
next_id = max([acc['id'] for acc in accounts]) + 1 if accounts else 1

# Utility Functions
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_balance(balance_str):
    """Validate and convert balance to float"""
    try:
        balance = float(balance_str)
        if balance < 0:
            return None, "Balance cannot be negative"
        if balance > 1000000:
            return None, "Balance too large"
        return round(balance, 2), None
    except (ValueError, TypeError):
        return None, "Invalid balance format"

def find_account(account_id):
    """Find account by ID"""
    return next((acc for acc in accounts if acc['id'] == account_id), None)

def calculate_dashboard_stats():
    """Calculate dashboard statistics"""
    total_accounts = len(accounts)
    active_accounts = len([acc for acc in accounts if acc['status'] == 'active'])
    total_balance = sum(acc['balance'] for acc in accounts)
    avg_balance = total_balance / total_accounts if total_accounts > 0 else 0
    
    return {
        'total_accounts': total_accounts,
        'active_accounts': active_accounts,
        'inactive_accounts': total_accounts - active_accounts,
        'total_balance': total_balance,
        'average_balance': avg_balance
    }

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

# Routes
@app.route('/')
def dashboard():
    """Main dashboard with account overview"""
    stats = calculate_dashboard_stats()
    recent_accounts = sorted(accounts, key=lambda x: x['created_date'], reverse=True)[:5]
    return render_template('dashboard.html', stats=stats, recent_accounts=recent_accounts)

@app.route('/accounts')
def list_accounts():
    """Display all accounts"""
    account_type_filter = request.args.get('type', '')
    status_filter = request.args.get('status', '')
    
    filtered_accounts = accounts
    
    if account_type_filter:
        filtered_accounts = [acc for acc in filtered_accounts 
                           if acc['account_type'] == account_type_filter]
    
    if status_filter:
        filtered_accounts = [acc for acc in filtered_accounts 
                           if acc['status'] == status_filter]
    
    return render_template('accounts.html', 
                         accounts=filtered_accounts,
                         account_type_filter=account_type_filter,
                         status_filter=status_filter)

@app.route('/account/<int:account_id>')
def view_account(account_id):
    """View single account details"""
    account = find_account(account_id)
    if not account:
        flash('Account not found', 'error')
        return redirect(url_for('list_accounts'))
    
    return render_template('account_detail.html', account=account)

@app.route('/account/create', methods=['GET', 'POST'])
def create_account():
    """Create new account"""
    global next_id
    
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        account_type = request.form.get('account_type', '')
        department = request.form.get('department', '').strip()
        balance_str = request.form.get('balance', '0')
        
        # Validation
        errors = []
        
        if not first_name:
            errors.append("First name is required")
        if not last_name:
            errors.append("Last name is required")
        if not email:
            errors.append("Email is required")
        elif not validate_email(email):
            errors.append("Invalid email format")
        elif any(acc['email'] == email for acc in accounts):
            errors.append("Email already exists")
        
        if not account_type or account_type not in ['basic', 'standard', 'premium']:
            errors.append("Valid account type is required")
        
        if not department:
            errors.append("Department is required")
        
        balance, balance_error = validate_balance(balance_str)
        if balance_error:
            errors.append(balance_error)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('account_form.html', 
                                 form_data=request.form,
                                 form_type='create')
        
        # Create account
        new_account = {
            'id': next_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'account_type': account_type,
            'department': department,
            'status': 'active',
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'balance': balance
        }
        
        accounts.append(new_account)
        next_id += 1
        
        flash(f'Account created successfully for {first_name} {last_name}!', 'success')
        return redirect(url_for('view_account', account_id=new_account['id']))
    
    return render_template('account_form.html', form_type='create')

@app.route('/account/<int:account_id>/edit', methods=['GET', 'POST'])
def edit_account(account_id):
    """Edit existing account"""
    account = find_account(account_id)
    if not account:
        flash('Account not found', 'error')
        return redirect(url_for('list_accounts'))
    
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        account_type = request.form.get('account_type', '')
        department = request.form.get('department', '').strip()
        status = request.form.get('status', '')
        balance_str = request.form.get('balance', '0')
        
        # Validation
        errors = []
        
        if not first_name:
            errors.append("First name is required")
        if not last_name:
            errors.append("Last name is required")
        if not email:
            errors.append("Email is required")
        elif not validate_email(email):
            errors.append("Invalid email format")
        elif any(acc['email'] == email and acc['id'] != account_id for acc in accounts):
            errors.append("Email already exists")
        
        if not account_type or account_type not in ['basic', 'standard', 'premium']:
            errors.append("Valid account type is required")
        
        if not department:
            errors.append("Department is required")
        
        if not status or status not in ['active', 'inactive']:
            errors.append("Valid status is required")
        
        balance, balance_error = validate_balance(balance_str)
        if balance_error:
            errors.append(balance_error)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('account_form.html', 
                                 account=account,
                                 form_data=request.form,
                                 form_type='edit')
        
        # Update account
        account.update({
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'account_type': account_type,
            'department': department,
            'status': status,
            'balance': balance
        })
        
        flash(f'Account updated successfully for {first_name} {last_name}!', 'success')
        return redirect(url_for('view_account', account_id=account_id))
    
    return render_template('account_form.html', account=account, form_type='edit')

@app.route('/account/<int:account_id>/delete', methods=['POST'])
def delete_account(account_id):
    """Delete account"""
    account = find_account(account_id)
    if not account:
        flash('Account not found', 'error')
        return redirect(url_for('list_accounts'))
    
    account_name = f"{account['first_name']} {account['last_name']}"
    accounts.remove(account)
    
    flash(f'Account for {account_name} has been deleted successfully', 'success')
    return redirect(url_for('list_accounts'))

# API Routes (RESTful endpoints)
@app.route('/api/accounts')
def api_list_accounts():
    """API endpoint to list all accounts"""
    return jsonify({
        'success': True,
        'count': len(accounts),
        'accounts': accounts
    })

@app.route('/api/account/<int:account_id>')
def api_get_account(account_id):
    """API endpoint to get single account"""
    account = find_account(account_id)
    if not account:
        return jsonify({'success': False, 'message': 'Account not found'}), 404
    
    return jsonify({'success': True, 'account': account})

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    return jsonify({
        'success': True,
        'stats': calculate_dashboard_stats()
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'accounts_count': len(accounts)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting AccountPro")
    print(f"📍 Running on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
