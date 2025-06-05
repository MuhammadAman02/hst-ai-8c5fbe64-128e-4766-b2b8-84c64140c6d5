"""
Irish Bank Fraud Detection System
Main application UI and routing
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

from nicegui import ui, app
from sqlalchemy.orm import Session

from core.database import get_db, init_db
from core.security import verify_password, create_access_token, get_password_hash
from models.schemas import Transaction, FraudAlert, User, TransactionCreate
from services.fraud_detection import FraudDetectionService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
fraud_service = None
current_user: Optional[User] = None

# Sample data for demonstration
SAMPLE_TRANSACTIONS = [
    {
        "id": "txn_001",
        "account_id": "acc_12345",
        "amount": 1500.00,
        "currency": "EUR",
        "merchant_name": "SuperValu Dublin",
        "merchant_category": "grocery",
        "location": "Dublin, Ireland",
        "timestamp": datetime.now() - timedelta(minutes=5),
        "card_last4": "1234",
        "transaction_type": "purchase"
    },
    {
        "id": "txn_002", 
        "account_id": "acc_12345",
        "amount": 5000.00,
        "currency": "EUR",
        "merchant_name": "Unknown Merchant",
        "merchant_category": "online",
        "location": "Lagos, Nigeria",
        "timestamp": datetime.now() - timedelta(minutes=2),
        "card_last4": "1234",
        "transaction_type": "purchase"
    },
    {
        "id": "txn_003",
        "account_id": "acc_67890", 
        "amount": 50.00,
        "currency": "EUR",
        "merchant_name": "Tesco Cork",
        "merchant_category": "grocery",
        "location": "Cork, Ireland",
        "timestamp": datetime.now() - timedelta(minutes=10),
        "card_last4": "5678",
        "transaction_type": "purchase"
    }
]

SAMPLE_ALERTS = [
    {
        "id": "alert_001",
        "transaction_id": "txn_002",
        "risk_score": 0.95,
        "alert_type": "high_risk_transaction",
        "description": "High-value transaction from unusual location",
        "status": "active",
        "created_at": datetime.now() - timedelta(minutes=2)
    }
]

async def initialize_data():
    """Initialize database and sample data"""
    try:
        logger.info("Initializing database and sample data...")
        
        # Initialize database
        init_db()
        
        # Initialize fraud detection service
        global fraud_service
        fraud_service = FraudDetectionService()
        
        logger.info("Application initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

def get_risk_color(risk_score: float) -> str:
    """Get color based on risk score"""
    if risk_score >= 0.7:
        return "red"
    elif risk_score >= 0.4:
        return "orange" 
    else:
        return "green"

def get_risk_level(risk_score: float) -> str:
    """Get risk level text"""
    if risk_score >= 0.7:
        return "HIGH"
    elif risk_score >= 0.4:
        return "MEDIUM"
    else:
        return "LOW"

@ui.page('/')
async def index():
    """Login page"""
    if current_user:
        ui.navigate.to('/dashboard')
        return
        
    with ui.card().classes('w-96 mx-auto mt-20'):
        ui.html('<div class="text-center mb-6"><h1 class="text-2xl font-bold text-blue-800">🏦 Irish Bank</h1><p class="text-gray-600">Fraud Detection System</p></div>')
        
        with ui.column().classes('w-full gap-4'):
            email_input = ui.input('Email', placeholder='admin@irishbank.ie').classes('w-full')
            password_input = ui.input('Password', password=True, placeholder='admin123').classes('w-full')
            
            async def handle_login():
                try:
                    email = email_input.value
                    password = password_input.value
                    
                    # Simple authentication for demo
                    if email == 'admin@irishbank.ie' and password == 'admin123':
                        global current_user
                        current_user = User(
                            id=1,
                            email=email,
                            full_name="Admin User",
                            role="admin",
                            is_active=True
                        )
                        ui.navigate.to('/dashboard')
                    else:
                        ui.notify('Invalid credentials', type='negative')
                        
                except Exception as e:
                    logger.error(f"Login error: {e}")
                    ui.notify('Login failed', type='negative')
            
            ui.button('Login', on_click=handle_login).classes('w-full bg-blue-600 text-white')

@ui.page('/dashboard')
async def dashboard():
    """Main dashboard"""
    if not current_user:
        ui.navigate.to('/')
        return
    
    # Header
    with ui.header().classes('bg-blue-800 text-white'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('🏦 Irish Bank - Fraud Detection').classes('text-xl font-bold')
            with ui.row().classes('items-center gap-4'):
                ui.label(f'Welcome, {current_user.full_name}')
                ui.button('Logout', on_click=lambda: [setattr(globals(), 'current_user', None), ui.navigate.to('/')]).classes('bg-red-600')
    
    # Main content
    with ui.column().classes('p-6 gap-6'):
        # Metrics row
        with ui.row().classes('w-full gap-4'):
            with ui.card().classes('flex-1 bg-green-50'):
                with ui.column().classes('items-center p-4'):
                    ui.label('Total Transactions Today').classes('text-sm text-gray-600')
                    ui.label('1,247').classes('text-2xl font-bold text-green-600')
            
            with ui.card().classes('flex-1 bg-orange-50'):
                with ui.column().classes('items-center p-4'):
                    ui.label('Fraud Alerts').classes('text-sm text-gray-600')
                    ui.label('3').classes('text-2xl font-bold text-orange-600')
            
            with ui.card().classes('flex-1 bg-red-50'):
                with ui.column().classes('items-center p-4'):
                    ui.label('High Risk Transactions').classes('text-sm text-gray-600')
                    ui.label('1').classes('text-2xl font-bold text-red-600')
            
            with ui.card().classes('flex-1 bg-blue-50'):
                with ui.column().classes('items-center p-4'):
                    ui.label('System Status').classes('text-sm text-gray-600')
                    ui.label('🟢 Online').classes('text-lg font-bold text-blue-600')
        
        # Recent Transactions
        with ui.card().classes('w-full'):
            ui.label('Recent Transactions').classes('text-xl font-bold mb-4')
            
            with ui.column().classes('w-full gap-2'):
                for txn_data in SAMPLE_TRANSACTIONS:
                    # Analyze transaction
                    if fraud_service:
                        try:
                            txn = Transaction(**txn_data)
                            analysis = fraud_service.analyze_transaction(txn)
                            risk_score = analysis.risk_score
                        except Exception as e:
                            logger.error(f"Error analyzing transaction: {e}")
                            risk_score = 0.1
                    else:
                        risk_score = 0.1
                    
                    risk_color = get_risk_color(risk_score)
                    risk_level = get_risk_level(risk_score)
                    
                    with ui.card().classes(f'w-full border-l-4 border-{risk_color}-500'):
                        with ui.row().classes('w-full items-center justify-between'):
                            with ui.column().classes('flex-1'):
                                with ui.row().classes('items-center gap-2'):
                                    ui.label(f"€{txn_data['amount']:,.2f}").classes('text-lg font-bold')
                                    ui.badge(risk_level, color=risk_color).classes('text-xs')
                                ui.label(f"{txn_data['merchant_name']} • {txn_data['location']}").classes('text-sm text-gray-600')
                                ui.label(f"Card ending {txn_data['card_last4']} • {txn_data['timestamp'].strftime('%H:%M')}").classes('text-xs text-gray-500')
                            
                            with ui.row().classes('gap-2'):
                                if risk_score >= 0.7:
                                    ui.button('🔍 Investigate', size='sm').classes('bg-orange-600 text-white')
                                    ui.button('🚫 Block', size='sm').classes('bg-red-600 text-white')
                                else:
                                    ui.button('✅ Approve', size='sm').classes('bg-green-600 text-white')
        
        # Active Alerts
        with ui.card().classes('w-full'):
            ui.label('Active Fraud Alerts').classes('text-xl font-bold mb-4')
            
            if SAMPLE_ALERTS:
                with ui.column().classes('w-full gap-2'):
                    for alert in SAMPLE_ALERTS:
                        with ui.card().classes('w-full border-l-4 border-red-500 bg-red-50'):
                            with ui.row().classes('w-full items-center justify-between'):
                                with ui.column().classes('flex-1'):
                                    ui.label(f"🚨 {alert['description']}").classes('font-bold text-red-800')
                                    ui.label(f"Transaction ID: {alert['transaction_id']}").classes('text-sm text-gray-600')
                                    ui.label(f"Risk Score: {alert['risk_score']:.2f} • {alert['created_at'].strftime('%H:%M')}").classes('text-xs text-gray-500')
                                
                                with ui.row().classes('gap-2'):
                                    ui.button('🔍 Investigate', size='sm').classes('bg-orange-600 text-white')
                                    ui.button('✅ Resolve', size='sm').classes('bg-green-600 text-white')
                                    ui.button('🚫 Block Account', size='sm').classes('bg-red-600 text-white')
            else:
                ui.label('No active alerts').classes('text-gray-500 italic')

@ui.page('/transactions')
async def transactions_page():
    """Transactions monitoring page"""
    if not current_user:
        ui.navigate.to('/')
        return
    
    with ui.header().classes('bg-blue-800 text-white'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('🏦 Irish Bank - Transaction Monitoring').classes('text-xl font-bold')
            ui.button('Dashboard', on_click=lambda: ui.navigate.to('/dashboard')).classes('bg-blue-600')
    
    with ui.column().classes('p-6 gap-6'):
        ui.label('Transaction Monitoring').classes('text-2xl font-bold')
        
        # Filters
        with ui.card().classes('w-full'):
            ui.label('Filters').classes('text-lg font-bold mb-4')
            with ui.row().classes('gap-4'):
                ui.select(['All', 'High Risk', 'Medium Risk', 'Low Risk'], value='All').classes('w-48')
                ui.select(['All', 'Last Hour', 'Last 24 Hours', 'Last Week'], value='Last 24 Hours').classes('w-48')
                ui.button('Apply Filters').classes('bg-blue-600 text-white')
        
        # Transaction list (detailed view)
        with ui.card().classes('w-full'):
            ui.label('All Transactions').classes('text-lg font-bold mb-4')
            
            # Table headers
            with ui.row().classes('w-full p-2 bg-gray-100 font-bold'):
                ui.label('Time').classes('w-24')
                ui.label('Amount').classes('w-24')
                ui.label('Merchant').classes('w-48')
                ui.label('Location').classes('w-32')
                ui.label('Risk').classes('w-24')
                ui.label('Actions').classes('w-32')
            
            # Transaction rows
            for txn_data in SAMPLE_TRANSACTIONS:
                if fraud_service:
                    try:
                        txn = Transaction(**txn_data)
                        analysis = fraud_service.analyze_transaction(txn)
                        risk_score = analysis.risk_score
                    except Exception as e:
                        logger.error(f"Error analyzing transaction: {e}")
                        risk_score = 0.1
                else:
                    risk_score = 0.1
                
                risk_color = get_risk_color(risk_score)
                risk_level = get_risk_level(risk_score)
                
                with ui.row().classes('w-full p-2 border-b hover:bg-gray-50'):
                    ui.label(txn_data['timestamp'].strftime('%H:%M')).classes('w-24 text-sm')
                    ui.label(f"€{txn_data['amount']:,.2f}").classes('w-24 font-bold')
                    ui.label(txn_data['merchant_name']).classes('w-48 text-sm')
                    ui.label(txn_data['location']).classes('w-32 text-sm')
                    ui.badge(risk_level, color=risk_color).classes('w-24')
                    with ui.row().classes('w-32 gap-1'):
                        ui.button('👁', size='sm').classes('bg-gray-600 text-white')
                        if risk_score >= 0.7:
                            ui.button('🚫', size='sm').classes('bg-red-600 text-white')

def main():
    """Main application entry point"""
    try:
        # Set up the app startup handler
        app.on_startup(initialize_data)
        
        # Configure UI settings
        ui.add_head_html('''
        <style>
            .nicegui-content { max-width: 100% !important; }
            body { font-family: 'Inter', sans-serif; }
        </style>
        ''')
        
        # Get port from environment
        port = int(os.getenv('PORT', 8000))
        
        # Run the application
        ui.run(
            host="0.0.0.0", 
            port=port, 
            title="Irish Bank Fraud Detection",
            favicon="🏦"
        )
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise

if __name__ == "__main__":
    main()