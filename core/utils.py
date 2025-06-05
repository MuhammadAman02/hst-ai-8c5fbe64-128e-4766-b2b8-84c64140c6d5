"""
Utility functions
"""
import hashlib
import secrets
import string
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_transaction_id() -> str:
    """Generate unique transaction ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"TXN{timestamp}{random_suffix}"


def calculate_hash(data: str) -> str:
    """Calculate SHA-256 hash of data"""
    return hashlib.sha256(data.encode()).hexdigest()


def format_currency(amount: float, currency: str = "EUR") -> str:
    """Format currency amount"""
    if currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"


def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    # Remove or replace unsafe characters
    sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
    return sanitized[:255]  # Limit length


def get_client_ip(request) -> str:
    """Get client IP address from request"""
    # Check for forwarded IP first (behind proxy)
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    
    # Check for real IP
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Fallback to remote address
    return getattr(request.client, 'host', 'unknown')


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data (e.g., credit card numbers)"""
    if len(data) <= visible_chars:
        return mask_char * len(data)
    
    return mask_char * (len(data) - visible_chars) + data[-visible_chars:]


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers"""
    import math
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


def is_business_hours(dt: datetime = None) -> bool:
    """Check if given datetime is within business hours (9 AM - 5 PM, Mon-Fri)"""
    if dt is None:
        dt = datetime.now()
    
    # Check if weekday (Monday = 0, Sunday = 6)
    if dt.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Check if within business hours
    return 9 <= dt.hour < 17


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string with fallback"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Failed to parse JSON: {json_str}")
        return default


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure"""
    import time
    import functools
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")
            
            raise last_exception
        
        return wrapper
    return decorator


class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"{self.description} completed in {duration:.2f}s")
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time is None:
            return 0.0
        
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()