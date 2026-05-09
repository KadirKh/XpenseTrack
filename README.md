# XpenseTrack

A comprehensive personal expense and income tracking web application built with Flask. XpenseTrack helps users manage their finances by tracking expenses, income, and maintaining a detailed history of their transactions.

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
- **Framework**: Flask 3.1.0
- **Database**: MySQL
- **ORM**: SQLAlchemy 2.0.38
- **Database Driver**: PyMySQL 1.1.1
- **Authentication**: Flask-Login 0.6.3

### Frontend
- **Templating**: Jinja2
- **Styling**: CSS

### Security
- **Password Hashing**: Werkzeug 3.1.3
- **Session Management**: Flask-Login

## Project Structure

```
XpenseTrack/
├── XpenseTrack.py          # Main application file
├── requirements.txt        # Project dependencies
├── README.md              # This file
│
├── static/                # Static files
│   ├── dashboard.css      # Dashboard styling
│   ├── login.css          # Login page styling
│   ├── styles.css         # General styling
│   └── profile_pics/      # User profile pictures (auto-created)
│
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Signup page
│   ├── login.html         # Login page
│   ├── dashboard.html     # Main dashboard
│   ├── profile.html       # User profile page
│   ├── edit_profile.html  # Edit profile page
│   ├── change_password.html # Change password page
│   └── edit_expense.html  # Edit expense page
│
└── Favicon/               # Favicon and manifest files
```

## Installation

### Prerequisites
- Python 3.x
- MySQL Server running locally
- pip (Python package manager)

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd XpenseTrack
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database**
   - Ensure MySQL is running on your local machine
   - Create a database named `xpensetrack`
   - The application will automatically create the required tables

   Modify the database configuration in `XpenseTrack.py`:
   ```python
   password = quote_plus("your_mysql_password")
   app.config["SQLALCHEMY_DATABASE_URI"] = (
       f"mysql+pymysql://root:{password}@localhost/xpensetrack"
   )
   ```

5. **Run the application**
   ```bash
   python XpenseTrack.py
   ```

   The application will be available at `http://localhost:5000`

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
- `id`: Primary key
- `name`: User's full name
- `email`: Email address (unique)
- `password`: Hashed password
- `join_date`: Account creation date

### Transaction Table
- `id`: Primary key
- `user_id`: Foreign key to user_info
- `date`: Transaction date
- `description`: Transaction description
- `category`: Transaction category
- `amount`: Transaction amount
- `type`: "expense" or "income"

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

- Passwords are hashed using Werkzeug security
- User sessions are managed securely
- Login required for protected routes
- CSRF protection through Flask
- User data isolation (users can only see their own data)

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
- Ensure MySQL is running: `mysql --version`
- Verify database credentials in `XpenseTrack.py`
- Check if database `xpensetrack` exists

### Import Errors
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Ensure virtual environment is activated

### Port Already in Use
- Flask uses port 5000 by default. If it's already in use, modify the port:
  ```python
  app.run(port=5001)
  ```

## Contributing

Feel free to fork this project and submit pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Contact

For questions or suggestions, please reach out to the project maintainer.

---

**Last Updated**: May 2026  
**Version**: 1.0.0
