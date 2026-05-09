"""
Database models for XpenseTrack application.
Defines User and Transaction models with proper relationships and methods.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model, UserMixin):
    """
    User model representing application users.
    
    Attributes:
        id (int): Primary key
        name (str): User's full name
        email (str): User's email (unique)
        password (str): Hashed password
        profile_pic (str): Path to profile picture
        join_date (datetime): Account creation timestamp
        transactions (list): Relationship to user's transactions
    """
    
    __tablename__ = "user_info"  # Keep table name for backward compatibility
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    profile_pic = db.Column(db.String(255), default=None)
    join_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    transactions = db.relationship("Transaction", backref="user", lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        """String representation of User instance."""
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
    
    def set_password(self, password):
        """
        Hash and set user password.
        
        Args:
            password (str): Plain text password
        """
        self.password = generate_password_hash(password)
    
    def verify_password(self, password):
        """
        Verify provided password against stored hash.
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password, password)
    
    def get_total_income(self):
        """
        Calculate user's total income across all transactions.
        
        Returns:
            float: Total income amount
        """
        result = db.session.query(db.func.sum(Transaction.amount)).filter_by(
            user_id=self.id, type="income"
        ).scalar()
        return float(result) if result else 0.0
    
    def get_total_expenses(self):
        """
        Calculate user's total expenses across all transactions.
        
        Returns:
            float: Total expenses amount
        """
        result = db.session.query(db.func.sum(Transaction.amount)).filter_by(
            user_id=self.id, type="expense"
        ).scalar()
        return float(result) if result else 0.0
    
    def get_balance(self):
        """
        Calculate user's balance (income - expenses).
        
        Returns:
            float: Current balance
        """
        return self.get_total_income() - self.get_total_expenses()


class Transaction(db.Model):
    """
    Transaction model for tracking income and expenses.
    
    Attributes:
        id (int): Primary key
        user_id (int): Foreign key to User
        date (datetime): Transaction date
        description (str): Transaction description
        category (str): Transaction category
        amount (float): Transaction amount
        type (str): "expense" or "income"
        created_at (datetime): Record creation timestamp
    """
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_info.id"), nullable=False, index=True)
    date = db.Column(db.DateTime, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # "expense" or "income"
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        """String representation of Transaction instance."""
        return f"<Transaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, type='{self.type}')>"
    
    def is_expense(self):
        """
        Check if transaction is an expense.
        
        Returns:
            bool: True if expense, False otherwise
        """
        return self.type == "expense"
    
    def is_income(self):
        """
        Check if transaction is income.
        
        Returns:
            bool: True if income, False otherwise
        """
        return self.type == "income"
    
    def to_dict(self):
        """
        Convert transaction to dictionary for API responses.
        
        Returns:
            dict: Transaction data as dictionary
        """
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d"),
            "description": self.description,
            "category": self.category,
            "amount": self.amount,
            "type": self.type,
        }
