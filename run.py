"""
Entry point for XpenseTrack application.
Creates and runs the Flask application with appropriate configuration.
"""

import os
from app import create_app

# Create app with appropriate configuration
config_name = os.getenv("FLASK_ENV", "development")
app = create_app(config_name)


if __name__ == "__main__":
    """Run the application."""
    debug_mode = os.getenv("DEBUG", "True") == "True"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
