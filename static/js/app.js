// Irish Bank Fraud Detection System JavaScript

class FraudDetectionApp {
    constructor() {
        this.isRealTimeEnabled = true;
        this.updateInterval = 5000; // 5 seconds
        this.charts = {};
        
        this.init();
    }
    
    init() {
        console.log('Irish Bank Fraud Detection System initialized');
        
        // Initialize real-time updates
        if (this.isRealTimeEnabled) {
            this.startRealTimeUpdates();
        }
        
        // Initialize event listeners
        this.initEventListeners();
        
        // Initialize tooltips
        this.initTooltips();
    }
    
    initEventListeners() {
        // Alert action buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('investigate-btn')) {
                this.handleInvestigateAlert(e.target.dataset.alertId);
            }
            
            if (e.target.classList.contains('block-btn')) {
                this.handleBlockTransaction(e.target.dataset.transactionId);
            }
            
            if (e.target.classList.contains('approve-btn')) {
                this.handleApproveTransaction(e.target.dataset.transactionId);
            }
        });
        
        // Search functionality
        const searchInput = document.getElementById('transaction-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterTransactions(e.target.value);
            });
        }
        
        // Real-time toggle
        const realtimeToggle = document.getElementById('realtime-toggle');
        if (realtimeToggle) {
            realtimeToggle.addEventListener('change', (e) => {
                this.toggleRealTime(e.target.checked);
            });
        }
    }
    
    initTooltips() {
        // Initialize tooltips for risk scores and other elements
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', this.showTooltip);
            element.addEventListener('mouseleave', this.hideTooltip);
        });
    }
    
    startRealTimeUpdates() {
        this.updateTimer = setInterval(() => {
            this.updateDashboard();
        }, this.updateInterval);
        
        console.log('Real-time updates started');
    }
    
    stopRealTimeUpdates() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
        
        console.log('Real-time updates stopped');
    }
    
    toggleRealTime(enabled) {
        this.isRealTimeEnabled = enabled;
        
        if (enabled) {
            this.startRealTimeUpdates();
        } else {
            this.stopRealTimeUpdates();
        }
        
        this.showNotification(
            enabled ? 'Real-time updates enabled' : 'Real-time updates disabled',
            enabled ? 'success' : 'info'
        );
    }
    
    async updateDashboard() {
        try {
            // Update metrics
            await this.updateMetrics();
            
            // Update recent transactions
            await this.updateRecentTransactions();
            
            // Update alerts
            await this.updateAlerts();
            
            // Update charts
            await this.updateCharts();
            
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }
    
    async updateMetrics() {
        // Simulate API call to get updated metrics
        const metrics = await this.fetchMetrics();
        
        // Update metric cards
        this.updateMetricCard('transactions-today', metrics.transactionsToday);
        this.updateMetricCard('fraud-detected', metrics.fraudDetected);
        this.updateMetricCard('amount-blocked', `€${metrics.amountBlocked.toLocaleString()}`);
        this.updateMetricCard('system-status', metrics.systemStatus);
    }
    
    updateMetricCard(cardId, value) {
        const card = document.getElementById(cardId);
        if (card) {
            const valueElement = card.querySelector('.metric-value');
            if (valueElement) {
                // Add animation class
                valueElement.classList.add('updating');
                
                setTimeout(() => {
                    valueElement.textContent = value;
                    valueElement.classList.remove('updating');
                }, 200);
            }
        }
    }
    
    async updateRecentTransactions() {
        const transactions = await this.fetchRecentTransactions();
        const container = document.getElementById('recent-transactions');
        
        if (container) {
            container.innerHTML = this.renderTransactions(transactions);
        }
    }
    
    async updateAlerts() {
        const alerts = await this.fetchActiveAlerts();
        const container = document.getElementById('active-alerts');
        
        if (container) {
            container.innerHTML = this.renderAlerts(alerts);
        }
    }
    
    async updateCharts() {
        // Update real-time monitoring chart
        const chartData = await this.fetchChartData();
        this.updateMonitoringChart(chartData);
    }
    
    renderTransactions(transactions) {
        return transactions.map(transaction => `
            <div class="transaction-row ${this.getRiskClass(transaction.riskScore)}" 
                 data-transaction-id="${transaction.id}">
                <div class="transaction-info">
                    <div class="amount">€${transaction.amount.toLocaleString()}</div>
                    <div class="merchant">${transaction.merchant}</div>
                    <div class="location">${transaction.location}</div>
                </div>
                <div class="transaction-meta">
                    <div class="risk-score" data-tooltip="Risk Score: ${transaction.riskScore}">
                        ${transaction.riskScore.toFixed(2)}
                    </div>
                    <div class="timestamp">${this.formatTime(transaction.timestamp)}</div>
                </div>
                <div class="transaction-actions">
                    ${this.renderTransactionActions(transaction)}
                </div>
            </div>
        `).join('');
    }
    
    renderAlerts(alerts) {
        if (alerts.length === 0) {
            return '<div class="no-alerts">No active alerts</div>';
        }
        
        return alerts.map(alert => `
            <div class="alert-card" data-alert-id="${alert.id}">
                <div class="alert-header">
                    <span class="alert-type">${alert.type}</span>
                    <span class="alert-time">${this.formatTime(alert.createdAt)}</span>
                </div>
                <div class="alert-details">
                    <div>Amount: €${alert.amount.toLocaleString()}</div>
                    <div>Risk Score: ${alert.riskScore.toFixed(2)}</div>
                    <div>Transaction: ${alert.transactionId}</div>
                </div>
                <div class="alert-actions">
                    <button class="btn btn-primary investigate-btn" 
                            data-alert-id="${alert.id}">
                        Investigate
                    </button>
                    <button class="btn btn-danger block-btn" 
                            data-transaction-id="${alert.transactionId}">
                        Block
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    renderTransactionActions(transaction) {
        if (transaction.riskScore > 0.7) {
            return `
                <button class="btn btn-danger block-btn" 
                        data-transaction-id="${transaction.id}">
                    Block
                </button>
                <button class="btn btn-warning investigate-btn" 
                        data-transaction-id="${transaction.id}">
                    Investigate
                </button>
            `;
        } else if (transaction.riskScore > 0.4) {
            return `
                <button class="btn btn-warning investigate-btn" 
                        data-transaction-id="${transaction.id}">
                    Review
                </button>
            `;
        } else {
            return `
                <button class="btn btn-primary approve-btn" 
                        data-transaction-id="${transaction.id}">
                    Approve
                </button>
            `;
        }
    }
    
    getRiskClass(riskScore) {
        if (riskScore > 0.7) return 'high-risk';
        if (riskScore > 0.4) return 'medium-risk';
        return 'low-risk';
    }
    
    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-IE', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    async handleInvestigateAlert(alertId) {
        try {
            this.showNotification('Starting investigation...', 'info');
            
            const result = await this.investigateAlert(alertId);
            
            if (result.success) {
                this.showNotification('Investigation started successfully', 'success');
                this.updateDashboard(); // Refresh data
            } else {
                this.showNotification('Failed to start investigation', 'error');
            }
        } catch (error) {
            console.error('Investigation error:', error);
            this.showNotification('Error starting investigation', 'error');
        }
    }
    
    async handleBlockTransaction(transactionId) {
        if (!confirm('Are you sure you want to block this transaction?')) {
            return;
        }
        
        try {
            this.showNotification('Blocking transaction...', 'info');
            
            const result = await this.blockTransaction(transactionId);
            
            if (result.success) {
                this.showNotification('Transaction blocked successfully', 'success');
                this.updateDashboard(); // Refresh data
            } else {
                this.showNotification('Failed to block transaction', 'error');
            }
        } catch (error) {
            console.error('Block transaction error:', error);
            this.showNotification('Error blocking transaction', 'error');
        }
    }
    
    async handleApproveTransaction(transactionId) {
        try {
            this.showNotification('Approving transaction...', 'info');
            
            const result = await this.approveTransaction(transactionId);
            
            if (result.success) {
                this.showNotification('Transaction approved successfully', 'success');
                this.updateDashboard(); // Refresh data
            } else {
                this.showNotification('Failed to approve transaction', 'error');
            }
        } catch (error) {
            console.error('Approve transaction error:', error);
            this.showNotification('Error approving transaction', 'error');
        }
    }
    
    filterTransactions(searchTerm) {
        const transactions = document.querySelectorAll('.transaction-row');
        const term = searchTerm.toLowerCase();
        
        transactions.forEach(transaction => {
            const text = transaction.textContent.toLowerCase();
            const matches = text.includes(term);
            
            transaction.style.display = matches ? 'block' : 'none';
        });
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Remove after delay
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    showTooltip(event) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = event.target.dataset.tooltip;
        
        document.body.appendChild(tooltip);
        
        const rect = event.target.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        
        event.target.tooltipElement = tooltip;
    }
    
    hideTooltip(event) {
        if (event.target.tooltipElement) {
            document.body.removeChild(event.target.tooltipElement);
            event.target.tooltipElement = null;
        }
    }
    
    // API Methods (mock implementations)
    async fetchMetrics() {
        // Simulate API call
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    transactionsToday: Math.floor(Math.random() * 100) + 1200,
                    fraudDetected: Math.floor(Math.random() * 10) + 20,
                    amountBlocked: Math.floor(Math.random() * 10000) + 40000,
                    systemStatus: 'Online'
                });
            }, 100);
        });
    }
    
    async fetchRecentTransactions() {
        // Simulate API call
        return new Promise(resolve => {
            setTimeout(() => {
                const transactions = [];
                for (let i = 0; i < 10; i++) {
                    transactions.push({
                        id: `TXN${1000 + i}`,
                        amount: Math.random() * 500 + 10,
                        merchant: ['Tesco', 'SuperValu', 'Amazon', 'PayPal'][Math.floor(Math.random() * 4)],
                        location: ['Dublin', 'Cork', 'Galway'][Math.floor(Math.random() * 3)],
                        riskScore: Math.random(),
                        timestamp: new Date(Date.now() - Math.random() * 3600000)
                    });
                }
                resolve(transactions);
            }, 100);
        });
    }
    
    async fetchActiveAlerts() {
        // Simulate API call
        return new Promise(resolve => {
            setTimeout(() => {
                const alerts = [];
                for (let i = 0; i < 3; i++) {
                    alerts.push({
                        id: `ALT${100 + i}`,
                        type: 'High Risk Transaction',
                        amount: Math.random() * 1000 + 500,
                        riskScore: Math.random() * 0.3 + 0.7,
                        transactionId: `TXN${2000 + i}`,
                        createdAt: new Date(Date.now() - Math.random() * 1800000)
                    });
                }
                resolve(alerts);
            }, 100);
        });
    }
    
    async fetchChartData() {
        // Simulate API call for chart data
        return new Promise(resolve => {
            setTimeout(() => {
                const data = {
                    timestamps: [],
                    transactionCounts: [],
                    riskScores: []
                };
                
                for (let i = 30; i > 0; i--) {
                    data.timestamps.push(new Date(Date.now() - i * 60000));
                    data.transactionCounts.push(Math.floor(Math.random() * 30) + 15);
                    data.riskScores.push(Math.random() * 0.5 + 0.2);
                }
                
                resolve(data);
            }, 100);
        });
    }
    
    async investigateAlert(alertId) {
        // Simulate API call
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({ success: true, message: 'Investigation started' });
            }, 500);
        });
    }
    
    async blockTransaction(transactionId) {
        // Simulate API call
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({ success: true, message: 'Transaction blocked' });
            }, 500);
        });
    }
    
    async approveTransaction(transactionId) {
        // Simulate API call
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({ success: true, message: 'Transaction approved' });
            }, 500);
        });
    }
    
    updateMonitoringChart(data) {
        // Update Plotly chart if it exists
        if (window.Plotly && this.charts.monitoring) {
            const update = {
                x: [data.timestamps],
                y: [data.transactionCounts]
            };
            
            Plotly.restyle('monitoring-chart', update, [0]);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.fraudApp = new FraudDetectionApp();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FraudDetectionApp;
}