# XpenseTrack

A comprehensive personal expense and income tracking web application built with Flask. XpenseTrack helps users manage their finances by tracking expenses, income, and maintaining a detailed history of their transactions.

## Quick Start

```bash
# 1. Clone and navigate to project
cd XpenseTrack

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with your MySQL credentials
# (See "Configure Environment Variables" section below)

# 5. Run the application
python run.py
```

Open http://localhost:5000 in your browser.

## Features

- **User Authentication**: Secure signup and login system with password hashing
- **Dashboard**: View monthly financial overview at a glance
  - Monthly income and expense totals
  - Current balance calculation
  - Recent transactions display
- **Expense Tracking**: Add, edit, and delete expenses with categorization
- **Income Tracking**: Record income sources and amounts
- **Transaction Management**: Full CRUD operations for all transactions
- **User Profile Management**: Update profile information and change password
- **Responsive UI**: Clean and intuitive user interface

## Tech Stack

### Backend
- **Framework**: Flask 3.1.0 - Lightweight Python web framework
- **Database**: MySQL 8.0+ - Relational database management system
- **ORM**: SQLAlchemy 2.0.38 - Object-Relational Mapping layer
- **Database Driver**: PyMySQL 1.1.1 - Pure Python MySQL client
- **Authentication**: Flask-Login 0.6.3 - User session management
- **CSRF Protection**: Flask-WTF 1.2.1 - Cross-Site Request Forgery protection
- **Password Hashing**: Werkzeug 3.1.3 - Security utilities including password hashing
- **XSS Prevention**: Bleach 6.1.0 - HTML sanitization library

### Frontend
- **Templating Engine**: Jinja2 - Template rendering for dynamic HTML
- **Styling**: CSS3 - Responsive design with custom stylesheets
- **Form Handling**: HTML5 forms with CSRF token protection

### Development Tools
- **Environment Management**: python-dotenv 1.0.0 - Load environment variables from .env
- **Logging**: Python built-in logging module - Application event logging

## Project Structure

```
XpenseTrack/
├── run.py                      # Application entry point
├── config.py                   # Configuration management (Dev/Prod/Test)
├── requirements.txt            # Project dependencies
├── .env                        # Environment variables (create this file)
├── README.md                   # This file
│
├── app/                        # Main application package
│   ├── __init__.py            # Flask app factory (create_app)
│   ├── models.py              # SQLAlchemy models (User, Transaction)
│   └── routes.py              # All route handlers (register_routes)
│
├── static/                     # Static files
│   ├── dashboard.css          # Dashboard styling
│   ├── login.css              # Login page styling
│   ├── styles.css             # General application styling
│   └── profile_pics/          # User profile pictures (auto-created)
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html              # Base template (navigation, footer)
│   ├── index.html             # Signup page
│   ├── login.html             # Login page
│   ├── dashboard.html         # Main dashboard with transaction forms
│   ├── profile.html           # User profile page
│   ├── edit_profile.html      # Profile editing and image upload
│   ├── change_password.html   # Password change form
│   └── edit_expense.html      # Expense editing page
│
├── Favicon/                    # Favicon and manifest files
│   ├── about.txt
│   └── site.webmanifest
│
└── logs/                       # Application logs (auto-created)
    └── app.log                # Debug and error logs
```

### Key Files Explained
- **run.py**: Entry point that creates the Flask app and starts the development server
- **app/__init__.py**: Application factory that configures Flask, database, login manager, and routes
- **app/models.py**: SQLAlchemy ORM models for User and Transaction tables
- **app/routes.py**: All HTTP route handlers wrapped in `register_routes(app)` function
- **config.py**: Configuration classes for different environments (development, production, testing)

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL Server 8.0+ running on `localhost:3306`
- pip (Python package manager)

### Setup Steps

#### 1. Clone or Download the Project
```bash
cd XpenseTrack
```

#### 2. Create a Virtual Environment (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_NAME=xpensetrack

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
DEBUG=True
```

**Note**: Replace `your_mysql_password` with your actual MySQL password.

#### 5. Set Up the Database
- Ensure MySQL Server is running
- The application will automatically create the database and tables on first run
- No manual database creation is needed

## Running the Project

### Option 1: Using run.py (Recommended)
```bash
python run.py
```

The application will start on `http://localhost:5000` or `http://127.0.0.1:5000`

### Option 2: Using Flask CLI
```bash
# Set Flask app
set FLASK_APP=run.py      # Windows
export FLASK_APP=run.py   # macOS/Linux

# Run in development mode
flask run
```

### Option 3: Direct Python Execution
```bash
python -c "from app import create_app; app = create_app('development'); app.run(debug=True)"
```

The application will display:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
 * Debugger PIN: xxx-xxx-xxx
```

Open your browser and navigate to `http://localhost:5000` to access XpenseTrack.

## Usage

### Getting Started
1. **Sign Up**: Create a new account with your name, email, and password
2. **Login**: Log in with your credentials
3. **Dashboard**: View your monthly financial summary

### Managing Expenses
- Click "Add Expense" to record a new expense
- Fill in:
  - Description (what was the expense for?)
  - Category (e.g., Food, Transport, Entertainment)
  - Amount
  - Date
- View all expenses for the current month on the dashboard
- Click on an expense to edit or delete it

### Managing Income
- Click "Add Income" to record income
- Fill in:
  - Date
  - Source (e.g., Salary, Freelance)
  - Amount
- View recent income entries on the dashboard

### Profile Management
- Navigate to Profile page to view and edit your information
- Update your name, email, and profile picture
- Change your password from the Change Password page

## Database Schema

### user_info Table
```sql
CREATE TABLE user_info (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(80) NOT NULL,
  email VARCHAR(200) UNIQUE NOT NULL,
  password VARCHAR(200) NOT NULL,
  profile_pic VARCHAR(255),
  join_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
- `id`: Primary key (auto-incremented)
- `name`: User's full name
- `email`: Email address (unique, indexed)
- `password`: Hashed password (bcrypt)
- `profile_pic`: Optional path to profile picture
- `join_date`: Account creation timestamp

### transaction Table
```sql
CREATE TABLE transaction (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  date DATE NOT NULL,
  description VARCHAR(255),
  category VARCHAR(50),
  amount DECIMAL(10, 2) NOT NULL,
  type ENUM('expense', 'income') NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user_info(id) ON DELETE CASCADE
);
```

**Columns:**
- `id`: Primary key (auto-incremented)
- `user_id`: Foreign key to user_info (cascade delete)
- `date`: Transaction date
- `description`: Transaction description/notes
- `category`: Category (e.g., "Food", "Transport", "Salary")
- `amount`: Transaction amount (decimal with 2 decimal places)
- `type`: Transaction type ("expense" or "income")

## Features Breakdown

### Authentication System
- Secure password hashing using Werkzeug
- Login required for all main features
- Session management with Flask-Login

### Dashboard Analytics
- Monthly income/expense totals
- Balance calculation (Income - Expenses)
- Recent transactions display (last 10)
- Filtered by current month and year

### Transaction Management
- Add new transactions with validation
- Edit existing transactions
- Delete transactions
- Category-based organization
- Date-based filtering

## Security Features

### Implemented Security Measures
- **Password Hashing**: Passwords are hashed using Werkzeug's `generate_password_hash()` and `check_password_hash()` with automatic salt generation
- **CSRF Protection**: Flask-WTF CSRF protection on all POST/PUT/DELETE requests via hidden form tokens
- **XSS Prevention**: User inputs sanitized using Bleach library with `clean()` function - all user-supplied content is stripped of HTML tags
- **Session Management**: Secure session handling with Flask-Login, automatic session cookies
- **User Isolation**: Users can only access and modify their own data
- **Protected Routes**: @login_required decorators on all sensitive endpoints
- **Input Validation**: Server-side validation on amount, date, and text fields
- **Secure Database Queries**: SQLAlchemy ORM prevents SQL injection attacks
- **Secure File Uploads**: Profile picture uploads restricted to allowed extensions (jpg, jpeg, png, gif, webp)

### Example Security Implementation
```python
# Password hashing
user.set_password("password123")  # Automatically hashed

# CSRF token on forms
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>

# XSS prevention
from bleach import clean
safe_text = sanitize_input(user_input)  # Strips HTML tags

# Protected routes
@login_required
def dashboard():
    # Only authenticated users can access
    pass
```

## Future Enhancements

Potential features for future versions:
- Export transactions to CSV/PDF
- Advanced filtering and search
- Recurring transaction templates
- Budget limits and alerts
- Multi-currency support
- Data visualization (charts and graphs)
- Mobile app version
- Dark mode
- Two-factor authentication

## Troubleshooting

### Database Connection Issues

**Error**: `pymysql.err.OperationalError: (1045, "Access denied for user 'root'@'localhost'")`

**Solution**:
- Verify MySQL is running: `mysql --version`
- Check MySQL server status and start it if needed
- Verify credentials in `.env` file match your MySQL installation
- Test MySQL connection:
  ```bash
  mysql -u root -p -h localhost
  ```

**Error**: `pymysql.err.OperationalError: (1049, "Unknown database 'xpensetrack'")`

**Solution**:
- The application automatically creates the database on first run
- Ensure you have permission to create databases
- Manually create database if needed: `CREATE DATABASE xpensetrack;`

### Missing Environment Variables

**Error**: `KeyError` or `ValueError` related to database configuration

**Solution**:
- Verify `.env` file exists in the project root
- Check all required variables are set (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, SECRET_KEY)
- Ensure no typos in variable names
- Restart the application after creating/updating `.env`

### Import and Dependency Errors

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
- Ensure virtual environment is activated:
  ```bash
  # Windows
  venv\Scripts\activate
  # macOS/Linux
  source venv/bin/activate
  ```
- Reinstall dependencies:
  ```bash
  pip install -r requirements.txt --force-reinstall
  ```

### Port Already in Use

**Error**: `Address already in use` or `Port 5000 in use`

**Solution**:
- Find and stop the process using port 5000:
  ```bash
  # Windows
  netstat -ano | findstr :5000
  taskkill /PID <PID> /F
  
  # macOS/Linux
  lsof -ti:5000 | xargs kill -9
  ```
- Or change the port in `run.py`:
  ```python
  if __name__ == "__main__":
      app.run(debug=True, port=5001)  # Use port 5001
  ```

### CSRF Token Errors

**Error**: `CSRF token is missing` or `Bad Request (400)`

**Solution**:
- Ensure all forms include the CSRF token:
  ```html
  <form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    <!-- form fields -->
  </form>
  ```
- Clear browser cookies and cache
- Restart the Flask application

### Database Schema Issues

**Error**: `Unknown column 'user_info.profile_pic' in 'field list'`

**Solution**:
- The database tables are out of sync with models
- Drop and recreate tables:
  ```python
  from app import create_app, db
  app = create_app('development')
  with app.app_context():
      db.drop_all()
      db.create_all()
  ```
- This will erase all data - use only for development

### Blank Page or Redirect Loop

**Error**: Pages not loading or continuous redirects

**Solution**:
- Check Flask debug output for errors
- Clear browser cookies: `Settings > Clear Browsing Data`
- Check logs in `logs/app.log` for detailed error messages
- Ensure FLASK_ENV=development in `.env`
- Verify all templates exist in `templates/` directory

### Login Issues

**Error**: "Invalid email or password" on correct credentials

**Solution**:
- Check email address case sensitivity (MySQL is case-insensitive by default)
- Verify user exists: Check database directly
- Clear session cookies and try again
- Check `logs/app.log` for authentication errors

## Contributing

Feel free to fork this project and submit pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Contact

For questions or suggestions, please reach out to the project maintainer.

---

**Last Updated**: May 2026  
**Version**: 1.0.0
