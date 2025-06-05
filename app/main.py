"""
Irish Bank Fraud Detection System
Main application with NiceGUI interface
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from nicegui import ui, app as nicegui_app
import os

from app.config import settings
from core.database import init_db, get_db_session
from core.security import get_current_user, create_access_token, verify_password
from services.fraud_detection import FraudDetectionService
from services.ml_models import MLModelService
from models.schemas import Transaction, User, FraudAlert
from app.components.monitoring import MonitoringDashboard
from app.components.auth import AuthComponent


class FraudDetectionApp:
    """Main fraud detection application"""
    
    def __init__(self):
        self.fraud_service = FraudDetectionService()
        self.ml_service = MLModelService()
        self.monitoring = MonitoringDashboard()
        self.auth = AuthComponent()
        self.current_user: Optional[User] = None
        self.is_authenticated = False
        
        # Initialize database
        init_db()
        
        # Setup UI theme
        self.setup_theme()
        
    def setup_theme(self):
        """Setup professional banking theme"""
        ui.add_head_html("""
        <style>
            :root {
                --primary-color: #1a365d;
                --secondary-color: #2d3748;
                --accent-color: #3182ce;
                --success-color: #38a169;
                --warning-color: #d69e2e;
                --danger-color: #e53e3e;
                --background-color: #f7fafc;
                --card-background: #ffffff;
                --text-primary: #2d3748;
                --text-secondary: #4a5568;
                --border-color: #e2e8f0;
            }
            
            .fraud-header {
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 1rem;
            }
            
            .risk-card {
                border-left: 4px solid var(--warning-color);
                background: var(--card-background);
                padding: 1rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .alert-card {
                border-left: 4px solid var(--danger-color);
                background: var(--card-background);
                padding: 1rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                animation: pulse 2s infinite;
            }
            
            .metric-card {
                background: var(--card-background);
                padding: 1.5rem;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
                border-top: 3px solid var(--accent-color);
            }
            
            .transaction-row {
                padding: 0.5rem;
                border-bottom: 1px solid var(--border-color);
                transition: background-color 0.2s;
            }
            
            .transaction-row:hover {
                background-color: #f8f9fa;
            }
            
            .high-risk {
                background-color: #fed7d7 !important;
            }
            
            .medium-risk {
                background-color: #fef5e7 !important;
            }
            
            .low-risk {
                background-color: #f0fff4 !important;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.7; }
                100% { opacity: 1; }
            }
            
            .status-indicator {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                display: inline-block;
                margin-right: 8px;
            }
            
            .status-online { background-color: var(--success-color); }
            .status-warning { background-color: var(--warning-color); }
            .status-offline { background-color: var(--danger-color); }
        </style>
        """)

    async def login_page(self):
        """Login page for authentication"""
        with ui.card().classes('w-96 mx-auto mt-20'):
            ui.html('<div class="fraud-header"><h2>🏦 Irish Bank Fraud Detection</h2><p>Secure Access Portal</p></div>')
            
            with ui.column().classes('w-full gap-4'):
                email_input = ui.input('Email', placeholder='admin@irishbank.ie').classes('w-full')
                password_input = ui.input('Password', password=True, placeholder='Enter password').classes('w-full')
                
                async def handle_login():
                    try:
                        # Simulate authentication (in production, verify against database)
                        if email_input.value == 'admin@irishbank.ie' and password_input.value == 'admin123':
                            self.current_user = User(
                                id=1,
                                email=email_input.value,
                                full_name="Bank Administrator",
                                role="admin",
                                is_active=True
                            )
                            self.is_authenticated = True
                            ui.navigate.to('/dashboard')
                        else:
                            ui.notification('Invalid credentials', type='negative')
                    except Exception as e:
                        ui.notification(f'Login error: {str(e)}', type='negative')
                
                ui.button('Login', on_click=handle_login).classes('w-full bg-blue-600 text-white')
                
                ui.separator()
                ui.label('Demo Credentials:').classes('text-sm text-gray-600')
                ui.label('Email: admin@irishbank.ie').classes('text-xs text-gray-500')
                ui.label('Password: admin123').classes('text-xs text-gray-500')

    async def dashboard_page(self):
        """Main fraud detection dashboard"""
        if not self.is_authenticated:
            ui.navigate.to('/login')
            return
            
        # Header
        with ui.row().classes('w-full items-center justify-between mb-4'):
            ui.html('<div class="fraud-header flex-1"><h1>🛡️ Fraud Detection Dashboard</h1><p>Real-time monitoring and analysis</p></div>')
            
            with ui.row().classes('items-center gap-4'):
                ui.label(f'Welcome, {self.current_user.full_name}').classes('text-sm')
                ui.button('Logout', on_click=lambda: ui.navigate.to('/login')).classes('bg-red-500 text-white')
        
        # Key Metrics Row
        with ui.row().classes('w-full gap-4 mb-6'):
            await self.create_metric_cards()
        
        # Main Content Grid
        with ui.row().classes('w-full gap-6'):
            # Left Column - Real-time Monitoring
            with ui.column().classes('flex-1'):
                await self.create_real_time_monitoring()
                await self.create_recent_transactions()
            
            # Right Column - Alerts and Analysis
            with ui.column().classes('flex-1'):
                await self.create_fraud_alerts()
                await self.create_risk_analysis()

    async def create_metric_cards(self):
        """Create key performance metric cards"""
        metrics = await self.fraud_service.get_daily_metrics()
        
        with ui.card().classes('metric-card'):
            ui.label('Transactions Today').classes('text-sm text-gray-600')
            ui.label(f'{metrics.get("transactions_today", 1247):,}').classes('text-2xl font-bold text-blue-600')
            ui.label('+12% from yesterday').classes('text-xs text-green-600')
        
        with ui.card().classes('metric-card'):
            ui.label('Fraud Detected').classes('text-sm text-gray-600')
            ui.label(f'{metrics.get("fraud_detected", 23)}').classes('text-2xl font-bold text-red-600')
            ui.label('0.18% fraud rate').classes('text-xs text-gray-500')
        
        with ui.card().classes('metric-card'):
            ui.label('Amount Blocked').classes('text-sm text-gray-600')
            ui.label(f'€{metrics.get("amount_blocked", 45670):,}').classes('text-2xl font-bold text-orange-600')
            ui.label('Potential losses prevented').classes('text-xs text-gray-500')
        
        with ui.card().classes('metric-card'):
            ui.label('System Status').classes('text-sm text-gray-600')
            with ui.row().classes('items-center'):
                ui.html('<span class="status-indicator status-online"></span>')
                ui.label('Online').classes('text-lg font-bold text-green-600')

    async def create_real_time_monitoring(self):
        """Create real-time transaction monitoring chart"""
        with ui.card().classes('w-full'):
            ui.label('Real-time Transaction Monitoring').classes('text-lg font-bold mb-4')
            
            # Generate sample real-time data
            df = await self.fraud_service.get_realtime_data()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['transaction_count'],
                mode='lines+markers',
                name='Transactions/min',
                line=dict(color='#3182ce', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['fraud_score'],
                mode='lines+markers',
                name='Avg Risk Score',
                yaxis='y2',
                line=dict(color='#e53e3e', width=2)
            ))
            
            fig.update_layout(
                title='Transaction Volume & Risk Trends',
                xaxis_title='Time',
                yaxis_title='Transactions per Minute',
                yaxis2=dict(
                    title='Average Risk Score',
                    overlaying='y',
                    side='right'
                ),
                height=300,
                showlegend=True
            )
            
            ui.plotly(fig).classes('w-full')

    async def create_recent_transactions(self):
        """Create recent transactions table with risk scoring"""
        with ui.card().classes('w-full mt-4'):
            ui.label('Recent Transactions').classes('text-lg font-bold mb-4')
            
            transactions = await self.fraud_service.get_recent_transactions()
            
            with ui.column().classes('w-full'):
                for transaction in transactions:
                    risk_class = self.get_risk_class(transaction['risk_score'])
                    
                    with ui.row().classes(f'transaction-row w-full {risk_class}'):
                        with ui.column().classes('flex-1'):
                            ui.label(f'€{transaction["amount"]:,.2f}').classes('font-bold')
                            ui.label(f'{transaction["merchant"]}').classes('text-sm text-gray-600')
                        
                        with ui.column().classes('flex-1'):
                            ui.label(f'Card: ****{transaction["card_last4"]}').classes('text-sm')
                            ui.label(f'{transaction["location"]}').classes('text-sm text-gray-600')
                        
                        with ui.column().classes('text-right'):
                            risk_score = transaction['risk_score']
                            risk_color = 'red' if risk_score > 0.7 else 'orange' if risk_score > 0.4 else 'green'
                            ui.label(f'Risk: {risk_score:.2f}').classes(f'font-bold text-{risk_color}-600')
                            ui.label(f'{transaction["timestamp"]}').classes('text-xs text-gray-500')

    async def create_fraud_alerts(self):
        """Create fraud alerts panel"""
        with ui.card().classes('w-full'):
            ui.label('🚨 Active Fraud Alerts').classes('text-lg font-bold mb-4')
            
            alerts = await self.fraud_service.get_active_alerts()
            
            if not alerts:
                ui.label('No active alerts').classes('text-gray-500 text-center py-8')
            else:
                for alert in alerts:
                    with ui.card().classes('alert-card mb-2'):
                        with ui.row().classes('w-full items-center justify-between'):
                            with ui.column():
                                ui.label(f'High Risk Transaction').classes('font-bold text-red-600')
                                ui.label(f'Amount: €{alert["amount"]:,.2f}').classes('text-sm')
                                ui.label(f'Card: ****{alert["card_last4"]}').classes('text-sm')
                                ui.label(f'Risk Score: {alert["risk_score"]:.2f}').classes('text-sm font-bold')
                            
                            with ui.column().classes('text-right'):
                                ui.button('Investigate', on_click=lambda a=alert: self.investigate_alert(a)).classes('bg-blue-600 text-white text-sm')
                                ui.button('Block', on_click=lambda a=alert: self.block_transaction(a)).classes('bg-red-600 text-white text-sm')

    async def create_risk_analysis(self):
        """Create risk analysis charts"""
        with ui.card().classes('w-full mt-4'):
            ui.label('Risk Analysis').classes('text-lg font-bold mb-4')
            
            # Risk distribution pie chart
            risk_data = await self.fraud_service.get_risk_distribution()
            
            fig = px.pie(
                values=list(risk_data.values()),
                names=list(risk_data.keys()),
                title='Risk Distribution (Last 24h)',
                color_discrete_map={
                    'Low Risk': '#38a169',
                    'Medium Risk': '#d69e2e',
                    'High Risk': '#e53e3e'
                }
            )
            fig.update_layout(height=300)
            
            ui.plotly(fig).classes('w-full')

    def get_risk_class(self, risk_score: float) -> str:
        """Get CSS class based on risk score"""
        if risk_score > 0.7:
            return 'high-risk'
        elif risk_score > 0.4:
            return 'medium-risk'
        else:
            return 'low-risk'

    async def investigate_alert(self, alert: Dict):
        """Handle alert investigation"""
        ui.notification(f'Investigating transaction {alert["transaction_id"]}', type='info')
        # In production, this would open detailed investigation view

    async def block_transaction(self, alert: Dict):
        """Handle transaction blocking"""
        ui.notification(f'Transaction {alert["transaction_id"]} blocked', type='warning')
        # In production, this would block the transaction and notify relevant parties

    async def health_check(self):
        """Health check endpoint"""
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Global app instance
fraud_app = FraudDetectionApp()


@ui.page('/')
async def index():
    """Root page - redirect to dashboard or login"""
    if fraud_app.is_authenticated:
        ui.navigate.to('/dashboard')
    else:
        ui.navigate.to('/login')


@ui.page('/login')
async def login():
    """Login page"""
    await fraud_app.login_page()


@ui.page('/dashboard')
async def dashboard():
    """Main dashboard page"""
    await fraud_app.dashboard_page()


# Health check endpoint
nicegui_app.add_route('/health', fraud_app.health_check)


def main():
    """Main application entry point"""
    ui.run(
        host=settings.host,
        port=settings.port,
        title=settings.app_name,
        favicon='🛡️',
        dark=False,
        show=False,
        reload=settings.debug
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()