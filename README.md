# Irish Bank Fraud Detection System

A sophisticated real-time fraud detection system designed for Irish banking institutions, featuring machine learning-based risk assessment, real-time transaction monitoring, and comprehensive security controls.

## 🚀 Features

- **Real-time Fraud Detection**: ML-powered transaction analysis with instant risk scoring
- **Interactive Dashboard**: Professional banking UI with live monitoring capabilities
- **Risk Assessment**: Multi-factor fraud scoring with customizable thresholds
- **Alert Management**: Instant notifications for suspicious activities
- **Compliance Ready**: GDPR and banking regulation compliant design
- **Audit Trail**: Complete transaction and user activity logging
- **Multi-user Support**: Role-based access for bank staff and analysts

## 🛡️ Security Features

- Enterprise-grade authentication and authorization
- Encrypted data storage and transmission
- Comprehensive audit logging
- Role-based access control
- Session management and timeout controls

## 📊 Analytics & Reporting

- Real-time transaction monitoring
- Fraud pattern analysis
- Risk trend visualization
- Compliance reporting
- Performance metrics dashboard

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd irish-bank-fraud-detection
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the system**
   - Open your browser to `http://localhost:8000`
   - Default admin credentials: admin@irishbank.ie / admin123

## 🐳 Docker Deployment

### Local Docker

```bash
# Build the image
docker build -t irish-bank-fraud-detection .

# Run the container
docker run -p 8000:8000 irish-bank-fraud-detection
```

### Fly.io Deployment

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy to Fly.io
fly deploy
```

## 🏗️ Architecture

```
├── app/                    # Main application
│   ├── main.py            # UI pages and components
│   ├── config.py          # Application configuration
│   └── components/        # Reusable UI components
├── api/                   # API endpoints
├── core/                  # Core functionality
│   ├── database.py        # Database connection
│   ├── security.py        # Security utilities
│   └── utils.py           # Utility functions
├── models/                # Data models
├── services/              # Business logic
│   ├── fraud_detection.py # Fraud detection engine
│   └── ml_models.py       # Machine learning models
└── static/                # Static assets
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FRAUD_THRESHOLD` | Fraud detection threshold (0-1) | 0.7 |
| `HIGH_RISK_THRESHOLD` | High risk alert threshold (0-1) | 0.9 |
| `DATABASE_URL` | Database connection string | sqlite:///./fraud_detection.db |
| `SECRET_KEY` | JWT secret key | Change in production |

### Fraud Detection Parameters

- **Transaction Amount Analysis**: Unusual spending patterns
- **Velocity Checks**: Rapid successive transactions
- **Geographic Analysis**: Location-based risk assessment
- **Behavioral Patterns**: User behavior deviation detection
- **Merchant Category**: High-risk merchant identification

## 📈 Monitoring & Alerts

### Real-time Monitoring

- Transaction volume and velocity
- Fraud detection accuracy metrics
- System performance indicators
- User activity patterns

### Alert Types

- **High Risk Transactions**: Score > 0.9
- **Suspicious Patterns**: Unusual behavior detected
- **System Alerts**: Performance or security issues
- **Compliance Alerts**: Regulatory requirement violations

## 🔒 Security Considerations

### Data Protection

- All sensitive data encrypted at rest and in transit
- PCI DSS compliance considerations
- GDPR data handling compliance
- Regular security audits and penetration testing

### Access Control

- Multi-factor authentication
- Role-based permissions
- Session timeout controls
- IP whitelisting capabilities

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

## 📝 API Documentation

### Authentication Endpoints

- `POST /api/auth/login` - User authentication
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Current user info

### Fraud Detection Endpoints

- `POST /api/fraud/analyze` - Analyze transaction for fraud
- `GET /api/fraud/alerts` - Get fraud alerts
- `GET /api/fraud/statistics` - Fraud detection statistics

### Monitoring Endpoints

- `GET /health` - Health check
- `GET /api/monitoring/metrics` - System metrics
- `GET /api/monitoring/status` - System status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Email: support@irishbank.ie
- Documentation: [Internal Wiki]
- Emergency: +353-1-XXX-XXXX

## 🔄 Version History

- **v1.0.0** - Initial release with core fraud detection
- Real-time monitoring dashboard
- ML-based risk scoring
- Enterprise security features

---

**Irish Bank Fraud Detection System** - Protecting Irish banking with advanced AI-powered fraud detection.