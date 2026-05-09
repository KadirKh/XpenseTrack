"""
Route handlers for XpenseTrack application.
Routes registered directly with Flask app (no blueprints for template compatibility).
"""

import os
from datetime import datetime
from bleach import clean
from flask import (
    render_template, request, redirect, url_for, flash, jsonify, current_app
)
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import extract
from app import db
from app.models import User, Transaction


def sanitize_input(text, strip=True):
    """Sanitize user input to prevent XSS attacks."""
    if not text:
        return ""
    text = clean(text, tags=[], strip_comments=True, strip=strip)
    return text.strip() if strip else text


def validate_amount(amount_str):
    """Validate and convert amount string to float."""
    if not amount_str:
        return False, None, "Amount is required"
    try:
        amount = float(amount_str)
    except ValueError:
        return False, None, "Invalid amount format"
    if amount <= 0:
        return False, None, "Amount must be greater than zero"
    if amount > 999999999:
        return False, None, "Amount exceeds maximum limit (999,999,999)"
    return True, amount, None


def validate_date(date_str, format="%Y-%m-%d"):
    """Validate and convert date string."""
    if not date_str:
        return False, None, "Date is required"
    try:
        date = datetime.strptime(date_str, format)
        return True, date, None
    except ValueError:
        return False, None, f"Invalid date format. Use {format}"


def allowed_file(filename):
    """Check if uploaded file has allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def register_routes(app):
    """Register all routes with the Flask app."""
    
    @app.route("/", methods=["GET", "POST"])
    def signup():
        """Handle user signup."""
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        
        if request.method == "POST":
            try:
                name = sanitize_input(request.form.get("name", ""))
                email = sanitize_input(request.form.get("email", ""))
                password = request.form.get("password", "")
                confirm_password = request.form.get("repassword", "")
                
                if not name or len(name) < 2:
                    flash("Name must be at least 2 characters long", "danger")
                    return redirect(url_for("signup"))
                
                if not email or "@" not in email:
                    flash("Please enter a valid email address", "danger")
                    return redirect(url_for("signup"))
                
                if not password or len(password) < 6:
                    flash("Password must be at least 6 characters long", "danger")
                    return redirect(url_for("signup"))
                
                if password != confirm_password:
                    flash("Passwords do not match", "danger")
                    return redirect(url_for("signup"))
                
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    flash("Email already registered. Please log in.", "warning")
                    return redirect(url_for("login"))
                
                user = User(name=name, email=email)
                user.set_password(password)
                
                db.session.add(user)
                db.session.commit()
                
                flash("Account created successfully! Please log in.", "success")
                return redirect(url_for("login"))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Signup error: {str(e)}", exc_info=True)
                flash("An error occurred during signup. Please try again.", "danger")
                return redirect(url_for("signup"))
        
        return render_template("index.html")
    
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Handle user login."""
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        
        if request.method == "POST":
            try:
                email = sanitize_input(request.form.get("email", ""))
                password = request.form.get("password", "")
                
                if not email or not password:
                    flash("Email and password are required", "danger")
                    return redirect(url_for("login"))
                
                user = User.query.filter_by(email=email).first()
                
                if user and user.verify_password(password):
                    login_user(user)
                    next_page = request.args.get("next")
                    return redirect(next_page) if next_page else redirect(url_for("dashboard"))
                
                flash("Invalid email or password", "danger")
                
            except Exception as e:
                current_app.logger.error(f"Login error: {str(e)}")
                flash("An error occurred during login. Please try again.", "danger")
        
        return render_template("login.html")
    
    
    @app.route("/logout")
    @login_required
    def logout():
        """Handle user logout."""
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))
    
    
    @app.route("/dashboard", methods=["GET"])
    @login_required
    def dashboard():
        """Display main dashboard."""
        try:
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            expenses = (
                Transaction.query.filter_by(user_id=current_user.id, type="expense")
                .filter(extract("month", Transaction.date) == current_month)
                .filter(extract("year", Transaction.date) == current_year)
                .order_by(Transaction.date.desc())
                .limit(10)
                .all()
            )
            
            incomes = (
                Transaction.query.filter_by(user_id=current_user.id, type="income")
                .filter(extract("month", Transaction.date) == current_month)
                .filter(extract("year", Transaction.date) == current_year)
                .order_by(Transaction.date.desc())
                .limit(10)
                .all()
            )
            
            monthly_expenses = current_user.get_total_expenses()
            monthly_income = current_user.get_total_income()
            balance = monthly_income - monthly_expenses
            
            return render_template(
                "dashboard.html",
                monthly_income=monthly_income,
                monthly_expenses=monthly_expenses,
                balance=balance,
                expenses=expenses,
                incomes=incomes,
            )
            
        except Exception as e:
            current_app.logger.error(f"Dashboard error: {str(e)}")
            flash("An error occurred loading the dashboard", "danger")
            return redirect(url_for("login"))
    
    
    @app.route("/add_expense", methods=["POST"])
    @login_required
    def add_expense():
        """Add a new expense transaction."""
        try:
            description = sanitize_input(request.form.get("description", ""))
            category = sanitize_input(request.form.get("category", ""))
            amount_str = request.form.get("amount", "")
            date_str = request.form.get("date", "")
            
            if not description or not category or not amount_str or not date_str:
                flash("Please fill in all fields", "danger")
                return redirect(url_for("dashboard"))
            
            is_valid, amount, error_msg = validate_amount(amount_str)
            if not is_valid:
                flash(error_msg, "danger")
                return redirect(url_for("dashboard"))
            
            is_valid, transaction_date, error_msg = validate_date(date_str)
            if not is_valid:
                flash(error_msg, "danger")
                return redirect(url_for("dashboard"))
            
            transaction = Transaction(
                user_id=current_user.id,
                description=description,
                category=category,
                amount=amount,
                date=transaction_date,
                type="expense",
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            flash("Expense added successfully!", "success")
            return redirect(url_for("dashboard"))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Add expense error: {str(e)}")
            flash("An error occurred while adding expense", "danger")
            return redirect(url_for("dashboard"))
    
    
    @app.route("/add_income", methods=["POST"])
    @login_required
    def add_income():
        """Add a new income transaction."""
        try:
            source = sanitize_input(request.form.get("source", ""))
            amount_str = request.form.get("amount", "")
            date_str = request.form.get("date", "")
            
            if not source or not amount_str or not date_str:
                flash("Please fill in all fields", "danger")
                return redirect(url_for("dashboard"))
            
            is_valid, amount, error_msg = validate_amount(amount_str)
            if not is_valid:
                flash(error_msg, "danger")
                return redirect(url_for("dashboard"))
            
            is_valid, transaction_date, error_msg = validate_date(date_str)
            if not is_valid:
                flash(error_msg, "danger")
                return redirect(url_for("dashboard"))
            
            transaction = Transaction(
                user_id=current_user.id,
                date=transaction_date,
                category=source,
                description="Income",
                amount=amount,
                type="income",
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            flash("Income added successfully!", "success")
            return redirect(url_for("dashboard"))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Add income error: {str(e)}")
            flash("An error occurred while adding income", "danger")
            return redirect(url_for("dashboard"))
    
    
    @app.route("/edit_expense/<int:id>", methods=["GET", "POST"])
    @login_required
    def edit_expense(id):
        """Edit an existing expense transaction."""
        try:
            transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first()
            
            if not transaction:
                flash("Expense not found or you don't have permission to edit it", "danger")
                return redirect(url_for("dashboard"))
            
            if request.method == "POST":
                description = sanitize_input(request.form.get("description", ""))
                category = sanitize_input(request.form.get("category", ""))
                amount_str = request.form.get("amount", "")
                date_str = request.form.get("date", "")
                
                if not description or not category or not amount_str or not date_str:
                    flash("Please fill in all fields", "danger")
                    return redirect(url_for("edit_expense", id=id))
                
                is_valid, amount, error_msg = validate_amount(amount_str)
                if not is_valid:
                    flash(error_msg, "danger")
                    return redirect(url_for("edit_expense", id=id))
                
                is_valid, transaction_date, error_msg = validate_date(date_str)
                if not is_valid:
                    flash(error_msg, "danger")
                    return redirect(url_for("edit_expense", id=id))
                
                transaction.description = description
                transaction.category = category
                transaction.amount = amount
                transaction.date = transaction_date
                
                db.session.commit()
                flash("Expense updated successfully!", "success")
                return redirect(url_for("dashboard"))
            
            return render_template("edit_expense.html", expense=transaction)
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Edit expense error: {str(e)}")
            flash("An error occurred while editing expense", "danger")
            return redirect(url_for("dashboard"))
    
    
    @app.route("/delete_expense/<int:id>", methods=["DELETE"])
    @login_required
    def delete_expense(id):
        """Delete an expense transaction."""
        try:
            transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first()
            
            if not transaction:
                return jsonify({"success": False, "error": "Unauthorized"}), 403
            
            db.session.delete(transaction)
            db.session.commit()
            
            return jsonify({"success": True, "message": "Expense deleted"})
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Delete expense error: {str(e)}")
            return jsonify({"success": False, "error": "An error occurred"}), 500
    
    
    @app.route("/profile")
    @login_required
    def profile():
        """Display user profile."""
        try:
            total_income = current_user.get_total_income()
            total_expenses = current_user.get_total_expenses()
            balance = current_user.get_balance()
            
            return render_template(
                "profile.html",
                total_income=total_income,
                total_expenses=total_expenses,
                balance=balance,
            )
            
        except Exception as e:
            current_app.logger.error(f"Profile error: {str(e)}")
            flash("An error occurred loading your profile", "danger")
            return redirect(url_for("dashboard"))
    
    
    @app.route("/edit_profile", methods=["GET", "POST"])
    @login_required
    def edit_profile():
        """Edit user profile information."""
        try:
            if request.method == "POST":
                name = sanitize_input(request.form.get("name", ""))
                email = sanitize_input(request.form.get("email", ""))
                
                if not name or len(name) < 2:
                    flash("Name must be at least 2 characters long", "danger")
                    return redirect(url_for("edit_profile"))
                
                existing_user = User.query.filter_by(email=email).filter(User.id != current_user.id).first()
                if existing_user:
                    flash("Email already in use", "danger")
                    return redirect(url_for("edit_profile"))
                
                current_user.name = name
                current_user.email = email
                
                if "profile_pic" in request.files:
                    file = request.files["profile_pic"]
                    if file and file.filename:
                        if allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
                            filename = timestamp + filename
                            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                            file.save(filepath)
                            current_user.profile_pic = f"profile_pics/{filename}"
                        else:
                            flash("Invalid file type. Allowed: png, jpg, jpeg, gif", "danger")
                            return redirect(url_for("edit_profile"))
                
                db.session.commit()
                flash("Profile updated successfully!", "success")
                return redirect(url_for("profile"))
            
            return render_template("edit_profile.html")
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Edit profile error: {str(e)}")
            flash("An error occurred while updating profile", "danger")
            return redirect(url_for("profile"))
    
    
    @app.route("/change_password", methods=["GET", "POST"])
    @login_required
    def change_password():
        """Change user password."""
        try:
            if request.method == "POST":
                current_password = request.form.get("current_password", "")
                new_password = request.form.get("new_password", "")
                confirm_password = request.form.get("confirm_new_password", "")
                
                if not current_user.verify_password(current_password):
                    flash("Current password is incorrect", "danger")
                    return redirect(url_for("change_password"))
                
                if not new_password or len(new_password) < 6:
                    flash("New password must be at least 6 characters long", "danger")
                    return redirect(url_for("change_password"))
                
                if new_password != confirm_password:
                    flash("New passwords do not match", "danger")
                    return redirect(url_for("change_password"))
                
                if current_password == new_password:
                    flash("New password must be different from current password", "danger")
                    return redirect(url_for("change_password"))
                
                current_user.set_password(new_password)
                db.session.commit()
                
                flash("Password changed successfully!", "success")
                return redirect(url_for("profile"))
            
            return render_template("change_password.html")
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Change password error: {str(e)}")
            flash("An error occurred while changing password", "danger")
            return redirect(url_for("profile"))
    
    
    @app.route("/expense_summary")
    @login_required
    def expense_summary():
        """Get expense summary by category."""
        try:
            category_data = (
                db.session.query(Transaction.category, db.func.sum(Transaction.amount))
                .filter_by(user_id=current_user.id, type="expense")
                .group_by(Transaction.category)
                .all()
            )
            
            data = {category: float(amount) for category, amount in category_data}
            return jsonify(data)
            
        except Exception as e:
            current_app.logger.error(f"Expense summary error: {str(e)}")
            return jsonify({"error": "An error occurred"}), 500
