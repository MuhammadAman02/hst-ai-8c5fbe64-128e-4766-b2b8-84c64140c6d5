"""
Irish Bank Fraud Detection System
Main application UI and routing
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np

from nicegui import ui, app
from services.fraud_detection import FraudDetectionService
from models.schemas import (
    Transaction, FraudAlert, User, UserLogin, SystemMetrics,
    Merchant, Card, Location, TransactionStatus, RiskLevel, AlertStatus
)
from core.security import SecurityService
from core.utils import generate_sample_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
fraud_service = FraudDetectionService()
security_service = SecurityService()

# Global state
current_user: Optional[User] = None
sample_transactions: List[Transaction] = []
sample_alerts: List[FraudAlert] = []
system_metrics: Optional[SystemMetrics] = None

# UI Theme
IRISH_BANK_THEME = {
    'primary': '#1a365d',      # Deep blue
    'secondary': '#2d3748',    # Dark gray
    'success': '#38a169',      # Green
    'warning': '#d69e2e',      # Orange
    'danger': '#e53e3e',       # Red
    'info': '#3182ce',         # Blue
    'light': '#f7fafc',        # Light gray
    'dark': '#1a202c'          # Very dark gray
}

async def initialize_data():
    """Initialize sample data for demonstration"""
    global sample_transactions, sample_alerts, system_metrics
    
    try:
        # Generate sample transactions
        sample_transactions = generate_sample_data(100)
        
        # Generate sample alerts
        sample_alerts = []
        for i, transaction in enumerate(sample_transactions[:10]):
            if transaction.risk_score and transaction.risk_score > 0.6:
                alert = FraudAlert(
                    id=f"ALERT_{i+1:03d}",
                    transaction_id=transaction.id,
                    alert_type="HIGH_RISK_TRANSACTION",
                    severity=RiskLevel.HIGH if transaction.risk_score > 0.8 else RiskLevel.MEDIUM,
                    status=AlertStatus.ACTIVE,
                    created_at=datetime.now() - timedelta(minutes=np.random.randint(1, 60)),
                    title=f"High Risk Transaction - €{transaction.amount:.2f}",
                    description=f"Suspicious transaction to {transaction.merchant.name}",
                    risk_score=transaction.risk_score,
                    triggered_rules=["High Amount", "Unusual Time", "Location Risk"]
                )
                sample_alerts.append(alert)
        
        # Get system metrics
        system_metrics = await fraud_service.get_system_metrics()
        
        logger.info(f"Initialized {len(sample_transactions)} transactions and {len(sample_alerts)} alerts")
        
    except Exception as e:
        logger.error(f"Error initializing data: {e}")

def create_header():
    """Create the application header"""
    with ui.header().classes('bg-blue-900 text-white shadow-lg'):
        with ui.row().classes('w-full items-center justify-between px-4'):
            with ui.row().classes('items-center'):
                ui.icon('security', size='2rem').classes('mr-2')
                ui.label('Irish Bank Fraud Detection').classes('text-xl font-bold')
            
            with ui.row().classes('items-center gap-4'):
                if current_user:
                    ui.label(f'Welcome, {current_user.full_name}').classes('text-sm')
                    ui.button('Logout', on_click=logout).props('flat').classes('text-white')
                
                # System status indicator
                with ui.row().classes('items-center gap-2'):
                    ui.icon('circle', size='sm').classes('text-green-400')
                    ui.label('System Online').classes('text-sm')

def create_sidebar():
    """Create the navigation sidebar"""
    with ui.left_drawer().classes('bg-gray-100'):
        with ui.column().classes('w-full p-4 gap-2'):
            ui.label('Navigation').classes('text-lg font-bold text-gray-700 mb-4')
            
            ui.button('Dashboard', on_click=lambda: ui.navigate.to('/dashboard')).props('flat').classes('w-full justify-start')
            ui.button('Transactions', on_click=lambda: ui.navigate.to('/transactions')).props('flat').classes('w-full justify-start')
            ui.button('Alerts', on_click=lambda: ui.navigate.to('/alerts')).props('flat').classes('w-full justify-start')
            ui.button('Analytics', on_click=lambda: ui.navigate.to('/analytics')).props('flat').classes('w-full justify-start')
            ui.button('Settings', on_click=lambda: ui.navigate.to('/settings')).props('flat').classes('w-full justify-start')

def create_metric_card(title: str, value: str, icon: str, color: str = 'blue'):
    """Create a metric display card"""
    with ui.card().classes(f'p-4 bg-{color}-50 border-l-4 border-{color}-500'):
        with ui.row().classes('items-center justify-between w-full'):
            with ui.column().classes('gap-1'):
                ui.label(title).classes(f'text-{color}-600 text-sm font-medium')
                ui.label(value).classes('text-2xl font-bold text-gray-900')
            ui.icon(icon, size='2rem').classes(f'text-{color}-500')

def create_transaction_table(transactions: List[Transaction]):
    """Create a transaction table"""
    columns = [
        {'name': 'id', 'label': 'Transaction ID', 'field': 'id', 'align': 'left'},
        {'name': 'amount', 'label': 'Amount', 'field': 'amount', 'align': 'right'},
        {'name': 'merchant', 'label': 'Merchant', 'field': 'merchant', 'align': 'left'},
        {'name': 'risk_score', 'label': 'Risk Score', 'field': 'risk_score', 'align': 'center'},
        {'name': 'status', 'label': 'Status', 'field': 'status', 'align': 'center'},
        {'name': 'timestamp', 'label': 'Time', 'field': 'timestamp', 'align': 'left'},
    ]
    
    rows = []
    for transaction in transactions[:20]:  # Show latest 20
        risk_color = 'red' if (transaction.risk_score or 0) > 0.7 else 'orange' if (transaction.risk_score or 0) > 0.4 else 'green'
        rows.append({
            'id': transaction.id[:12] + '...',
            'amount': f'€{transaction.amount:.2f}',
            'merchant': transaction.merchant.name,
            'risk_score': f'{(transaction.risk_score or 0):.2f}',
            'status': transaction.status.value,
            'timestamp': transaction.timestamp.strftime('%H:%M:%S'),
            'risk_color': risk_color
        })
    
    with ui.card().classes('w-full'):
        ui.label('Recent Transactions').classes('text-lg font-bold mb-4')
        
        table = ui.table(columns=columns, rows=rows).classes('w-full')
        table.add_slot('body-cell-risk_score', '''
            <q-td :props="props">
                <q-badge :color="props.row.risk_color" :label="props.value" />
            </q-td>
        ''')

def create_alert_list(alerts: List[FraudAlert]):
    """Create an alert list"""
    with ui.card().classes('w-full'):
        ui.label('Active Fraud Alerts').classes('text-lg font-bold mb-4')
        
        if not alerts:
            ui.label('No active alerts').classes('text-gray-500 text-center p-4')
            return
        
        for alert in alerts[:10]:  # Show latest 10
            severity_color = {
                RiskLevel.CRITICAL: 'red',
                RiskLevel.HIGH: 'orange',
                RiskLevel.MEDIUM: 'yellow',
                RiskLevel.LOW: 'green'
            }.get(alert.severity, 'gray')
            
            with ui.card().classes(f'mb-2 border-l-4 border-{severity_color}-500'):
                with ui.row().classes('items-center justify-between w-full p-2'):
                    with ui.column().classes('gap-1 flex-grow'):
                        ui.label(alert.title).classes('font-medium')
                        ui.label(alert.description).classes('text-sm text-gray-600')
                        ui.label(f'Risk Score: {alert.risk_score:.2f}').classes('text-xs text-gray-500')
                    
                    with ui.column().classes('gap-1 items-end'):
                        ui.badge(alert.severity.value.upper()).props(f'color={severity_color}')
                        ui.label(alert.created_at.strftime('%H:%M')).classes('text-xs text-gray-500')
                        
                        with ui.row().classes('gap-1'):
                            ui.button('Investigate', size='sm').props('dense flat')
                            ui.button('Block', size='sm').props('dense flat color=red')

async def logout():
    """Handle user logout"""
    global current_user
    current_user = None
    ui.navigate.to('/login')

@ui.page('/login')
async def login_page():
    """Login page"""
    ui.add_head_html('<title>Irish Bank Fraud Detection - Login</title>')
    
    with ui.column().classes('items-center justify-center min-h-screen bg-gray-100'):
        with ui.card().classes('p-8 max-w-md w-full'):
            with ui.column().classes('items-center gap-4 w-full'):
                ui.icon('security', size='3rem').classes('text-blue-900')
                ui.label('Irish Bank Fraud Detection').classes('text-xl font-bold text-center')
                ui.label('Secure Login').classes('text-gray-600 text-center')
                
                email_input = ui.input('Email', placeholder='admin@irishbank.ie').classes('w-full')
                password_input = ui.input('Password', password=True, placeholder='admin123').classes('w-full')
                
                async def handle_login():
                    global current_user
                    try:
                        # Simulate authentication
                        if email_input.value == 'admin@irishbank.ie' and password_input.value == 'admin123':
                            current_user = User(
                                id='admin_001',
                                email=email_input.value,
                                full_name='System Administrator',
                                role='admin',
                                created_at=datetime.now()
                            )
                            ui.notify('Login successful!', type='positive')
                            ui.navigate.to('/dashboard')
                        else:
                            ui.notify('Invalid credentials', type='negative')
                    except Exception as e:
                        logger.error(f"Login error: {e}")
                        ui.notify('Login failed', type='negative')
                
                ui.button('Login', on_click=handle_login).classes('w-full bg-blue-900 text-white')
                
                ui.separator()
                ui.label('Demo Credentials:').classes('text-sm text-gray-600')
                ui.label('Email: admin@irishbank.ie').classes('text-xs text-gray-500')
                ui.label('Password: admin123').classes('text-xs text-gray-500')

@ui.page('/dashboard')
async def dashboard_page():
    """Main dashboard page"""
    if not current_user:
        ui.navigate.to('/login')
        return
    
    ui.add_head_html('<title>Dashboard - Irish Bank Fraud Detection</title>')
    
    create_header()
    create_sidebar()
    
    with ui.column().classes('p-6 gap-6'):
        ui.label('Fraud Detection Dashboard').classes('text-2xl font-bold text-gray-900')
        
        # Metrics row
        if system_metrics:
            with ui.row().classes('gap-4 w-full'):
                create_metric_card('Total Transactions', f'{system_metrics.total_transactions:,}', 'receipt', 'blue')
                create_metric_card('Fraud Detected', f'{system_metrics.fraud_detected}', 'warning', 'red')
                create_metric_card('Active Alerts', f'{system_metrics.active_alerts}', 'notifications', 'orange')
                create_metric_card('Model Accuracy', f'{system_metrics.model_accuracy:.1%}', 'analytics', 'green')
        
        # Charts and tables row
        with ui.row().classes('gap-6 w-full'):
            with ui.column().classes('flex-1'):
                create_transaction_table(sample_transactions)
            
            with ui.column().classes('flex-1'):
                create_alert_list(sample_alerts)

@ui.page('/transactions')
async def transactions_page():
    """Transactions monitoring page"""
    if not current_user:
        ui.navigate.to('/login')
        return
    
    ui.add_head_html('<title>Transactions - Irish Bank Fraud Detection</title>')
    
    create_header()
    create_sidebar()
    
    with ui.column().classes('p-6 gap-6'):
        ui.label('Transaction Monitoring').classes('text-2xl font-bold text-gray-900')
        
        # Filters
        with ui.card().classes('p-4 w-full'):
            with ui.row().classes('gap-4 items-end'):
                ui.input('Search Transaction ID').classes('flex-1')
                ui.select(['All', 'High Risk', 'Medium Risk', 'Low Risk'], value='All', label='Risk Level').classes('w-48')
                ui.select(['All', 'Pending', 'Approved', 'Declined', 'Blocked'], value='All', label='Status').classes('w-48')
                ui.button('Filter', icon='filter_list').props('color=primary')
        
        # Transaction table
        create_transaction_table(sample_transactions)

@ui.page('/alerts')
async def alerts_page():
    """Fraud alerts page"""
    if not current_user:
        ui.navigate.to('/login')
        return
    
    ui.add_head_html('<title>Alerts - Irish Bank Fraud Detection</title>')
    
    create_header()
    create_sidebar()
    
    with ui.column().classes('p-6 gap-6'):
        ui.label('Fraud Alerts Management').classes('text-2xl font-bold text-gray-900')
        
        # Alert filters
        with ui.card().classes('p-4 w-full'):
            with ui.row().classes('gap-4 items-end'):
                ui.select(['All', 'Active', 'Investigating', 'Resolved'], value='Active', label='Status').classes('w-48')
                ui.select(['All', 'Critical', 'High', 'Medium', 'Low'], value='All', label='Severity').classes('w-48')
                ui.button('Refresh', icon='refresh').props('color=primary')
        
        # Alert list
        create_alert_list(sample_alerts)

@ui.page('/analytics')
async def analytics_page():
    """Analytics and reporting page"""
    if not current_user:
        ui.navigate.to('/login')
        return
    
    ui.add_head_html('<title>Analytics - Irish Bank Fraud Detection</title>')
    
    create_header()
    create_sidebar()
    
    with ui.column().classes('p-6 gap-6'):
        ui.label('Fraud Analytics & Reports').classes('text-2xl font-bold text-gray-900')
        
        with ui.row().classes('gap-6 w-full'):
            # Model performance
            with ui.card().classes('p-4 flex-1'):
                ui.label('Model Performance').classes('text-lg font-bold mb-4')
                ui.label('Accuracy: 95.2%').classes('text-green-600 font-medium')
                ui.label('Precision: 94.8%').classes('text-blue-600 font-medium')
                ui.label('Recall: 93.1%').classes('text-purple-600 font-medium')
                ui.label('F1-Score: 93.9%').classes('text-orange-600 font-medium')
            
            # Fraud trends
            with ui.card().classes('p-4 flex-1'):
                ui.label('Fraud Trends (Last 30 Days)').classes('text-lg font-bold mb-4')
                ui.label('Total Fraud Cases: 127').classes('text-red-600 font-medium')
                ui.label('Amount Saved: €2.4M').classes('text-green-600 font-medium')
                ui.label('False Positives: 8.2%').classes('text-yellow-600 font-medium')
                ui.label('Response Time: 0.15s avg').classes('text-blue-600 font-medium')

@ui.page('/settings')
async def settings_page():
    """Settings and configuration page"""
    if not current_user:
        ui.navigate.to('/login')
        return
    
    ui.add_head_html('<title>Settings - Irish Bank Fraud Detection</title>')
    
    create_header()
    create_sidebar()
    
    with ui.column().classes('p-6 gap-6'):
        ui.label('System Settings').classes('text-2xl font-bold text-gray-900')
        
        with ui.row().classes('gap-6 w-full'):
            # Model settings
            with ui.card().classes('p-4 flex-1'):
                ui.label('Model Configuration').classes('text-lg font-bold mb-4')
                ui.number('Risk Threshold', value=0.7, min=0, max=1, step=0.1).classes('w-full')
                ui.number('Alert Threshold', value=0.8, min=0, max=1, step=0.1).classes('w-full')
                ui.switch('Auto-block High Risk', value=True)
                ui.switch('Real-time Monitoring', value=True)
                ui.button('Save Settings').props('color=primary')
            
            # System status
            with ui.card().classes('p-4 flex-1'):
                ui.label('System Status').classes('text-lg font-bold mb-4')
                ui.label('Model Version: 1.0.0').classes('text-gray-600')
                ui.label('Last Training: 2024-01-15').classes('text-gray-600')
                ui.label('Database Status: Connected').classes('text-green-600')
                ui.label('API Status: Online').classes('text-green-600')
                ui.button('Retrain Model').props('color=orange')

@ui.page('/')
async def index():
    """Root page - redirect to dashboard or login"""
    if current_user:
        ui.navigate.to('/dashboard')
    else:
        ui.navigate.to('/login')

def main():
    """Main application entry point"""
    try:
        # Initialize data
        asyncio.create_task(initialize_data())
        
        # Configure NiceGUI
        ui.run(
            title='Irish Bank Fraud Detection System',
            port=int(os.environ.get('PORT', 8000)),
            host='0.0.0.0',
            reload=False,
            show=False,
            favicon='🏦'
        )
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise

if __name__ == "__main__":
    main()