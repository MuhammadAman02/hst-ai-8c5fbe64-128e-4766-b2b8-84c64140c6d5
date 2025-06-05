"""
Irish Bank Fraud Detection System
Entry point for the application
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import and run the application
from app.main import main

if __name__ == "__main__":
    main()