import random
import string
from datetime import datetime, timedelta

def generate_validation_code():
    code = ''.join(random.choices(string.digits, k=6))  # Generate a 6-digit code
    return code

def get_consecutive_dates():
    today = datetime.now().date()
    return [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(3)]