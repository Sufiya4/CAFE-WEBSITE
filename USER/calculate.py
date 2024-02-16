from datetime import datetime, timedelta

def get_consecutive_dates():
    today = datetime.now().date()
    return [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(3)]