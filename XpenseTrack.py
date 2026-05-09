from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.sql import func
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from urllib.parse import quote_plus
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-key-change-in-production")
csrf = CSRFProtect(app)

# Database Configuration
db_user = os.getenv("DB_USER", "root")
db_password = quote_plus(os.getenv("DB_PASSWORD", ""))
db_host = os.getenv("DB_HOST", "localhost")
db_name = os.getenv("DB_NAME", "xpensetrack")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/profile_pics"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return user_info.query.get(int(user_id))


class user_info(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_pic = db.Column(db.String(255), default=None)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<user_info(id={self.id}, name='{self.name}', email='{self.email}')>"


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return (
            f"<Transaction(id={self.id}, user_id={self.user_id}, amount={self.amount})>"
        )


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        repassword = request.form.get("repassword")

        existing_user = user_info.query.filter_by(email=email).first()
        if existing_user:
            # flash("Email already registered. Please log in.", "warning")
            return redirect(url_for("login"))

        if password != repassword:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)
        new_user = user_info(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        return redirect(url_for("login"))

    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = user_info.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid email or password", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    # Get current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Fetch recent expenses for the current month
    expenses = (
        Transaction.query.filter_by(user_id=current_user.id, type="expense")
        .filter(db.extract("month", Transaction.date) == current_month)
        .filter(db.extract("year", Transaction.date) == current_year)
        .order_by(Transaction.date.desc())
        .limit(10)
        .all()
    )

    # Fetch recent incomes for the current month
    incomes = (
        Transaction.query.filter_by(user_id=current_user.id, type="income")
        .filter(db.extract("month", Transaction.date) == current_month)
        .filter(db.extract("year", Transaction.date) == current_year)
        .order_by(Transaction.date.desc())
        .limit(10)
        .all()
    )

    # Calculate total expenses for the current month
    monthly_expenses = (
        db.session.query(db.func.sum(Transaction.amount))
        .filter_by(user_id=current_user.id, type="expense")
        .filter(db.extract("month", Transaction.date) == current_month)
        .filter(db.extract("year", Transaction.date) == current_year)
        .scalar()
        or 0
    )

    # Calculate total income for the current month
    monthly_income = (
        db.session.query(db.func.sum(Transaction.amount))
        .filter_by(user_id=current_user.id, type="income")
        .filter(db.extract("month", Transaction.date) == current_month)
        .filter(db.extract("year", Transaction.date) == current_year)
        .scalar()
        or 0
    )

    # Calculate balance (Income - Expenses)
    balance = monthly_income - monthly_expenses

    return render_template(
        "dashboard.html",
        user=current_user,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        balance=balance,
        expenses=expenses,
        incomes=incomes,
    )


@app.route("/add_expense", methods=["POST"])
@login_required
def add_expense():
    description = request.form.get("description")
    category = request.form.get("category")
    amount = request.form.get("amount")
    date_str = request.form.get("date")

    if not description or not category or not amount or not date_str:
        flash("Please fill in all fields!", "danger")
        return redirect(url_for("dashboard"))

    try:
        amount = float(amount)
        if amount <= 0:
            flash("Amount must be greater than zero!", "danger")
            return redirect(url_for("dashboard"))
        if amount > 999999999:
            flash("Amount exceeds maximum limit!", "danger")
            return redirect(url_for("dashboard"))
    except ValueError:
        flash("Invalid amount entered!", "danger")
        return redirect(url_for("dashboard"))

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format!", "danger")
        return redirect(url_for("dashboard"))

    new_expense = Transaction(
        user_id=current_user.id,
        description=description,
        category=category,
        amount=amount,
        date=date,
        type="expense",
    )

    db.session.add(new_expense)
    db.session.commit()

    flash("Expense added successfully!", "success")
    return redirect(url_for("dashboard"))


@app.route("/add_income", methods=["POST"])
@login_required
def add_income():
    date = request.form.get("date")
    source = request.form.get("source")
    amount = request.form.get("amount")

    if not date or not source or not amount:
        flash("All fields are required!", "danger")
        return redirect(url_for("dashboard"))

    try:
        amount = float(amount)
        if amount <= 0:
            flash("Amount must be greater than zero!", "danger")
            return redirect(url_for("dashboard"))
        if amount > 999999999:
            flash("Amount exceeds maximum limit!", "danger")
            return redirect(url_for("dashboard"))
    except ValueError:
        flash("Invalid amount!", "danger")
        return redirect(url_for("dashboard"))

    new_income = Transaction(
        user_id=current_user.id,
        date=datetime.strptime(date, "%Y-%m-%d"),
        category=source,
        description="Income",
        amount=amount,
        type="income",
    )
    db.session.add(new_income)
    db.session.commit()

    flash("Income added successfully!", "success")
    return redirect(url_for("dashboard"))


@app.route("/edit_expense/<int:id>", methods=["GET", "POST"])
@login_required
def edit_expense(id):
    expense = Transaction.query.filter_by(id=id, user_id=current_user.id).first()

    if not expense:
        flash("Expense not found!", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        expense.description = request.form.get("description")
        expense.category = request.form.get("category")
        amount = request.form.get("amount")
        date_str = request.form.get("date")

        if (
            not expense.description
            or not expense.category
            or not amount
            or not date_str
        ):
            flash("Please fill in all fields!", "danger")
            return redirect(url_for("edit_expense", id=id))

        try:
            expense.amount = float(amount)
            if expense.amount <= 0:
                flash("Amount must be greater than zero!", "danger")
                return redirect(url_for("edit_expense", id=id))
            if expense.amount > 999999999:
                flash("Amount exceeds maximum limit!", "danger")
                return redirect(url_for("edit_expense", id=id))
        except ValueError:
            flash("Invalid amount entered!", "danger")
            return redirect(url_for("edit_expense", id=id))

        try:
            expense.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format!", "danger")
            return redirect(url_for("edit_expense", id=id))

        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("edit_expense.html", expense=expense)


@app.route("/delete_expense/<int:id>", methods=["DELETE"])
@login_required
def delete_expense(id):
    expense = Transaction.query.get_or_404(id)

    if expense.user_id != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    db.session.delete(expense)
    db.session.commit()
    return jsonify({"success": True})


@app.route("/profile")
@login_required
def profile():
    total_income = (
        db.session.query(db.func.sum(Transaction.amount))
        .filter_by(user_id=current_user.id, type="income")
        .scalar()
        or 0
    )
    total_expenses = (
        db.session.query(db.func.sum(Transaction.amount))
        .filter_by(user_id=current_user.id, type="expense")
        .scalar()
        or 0
    )
    balance = total_income - total_expenses

    return render_template(
        "profile.html",
        user=current_user,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
    )


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.name = request.form.get("name")
        current_user.email = request.form.get("email")

        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                current_user.profile_pic = f"profile_pics/{filename}"

        db.session.commit()
        return redirect(url_for("profile"))

    return render_template("edit_profile.html", user=current_user)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_new_password = request.form.get("confirm_new_password")

        if not check_password_hash(current_user.password, current_password):
            flash("Current password is incorrect!", "danger")
            return redirect(url_for("change_password"))

        if new_password != confirm_new_password:
            flash("New passwords do not match!", "danger")
            return redirect(url_for("change_password"))

        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        flash("Password changed successfully!", "success")
        return redirect(url_for("profile"))

    return render_template("change_password.html")


@app.route("/expense_summary")
@login_required
def expense_summary():
    category_data = (
        db.session.query(Transaction.category, func.sum(Transaction.amount))
        .filter_by(user_id=current_user.id, type="expense")
        .group_by(Transaction.category)
        .all()
    )

    data = {category: float(amount) for category, amount in category_data}
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=False, use_reloader=True)
