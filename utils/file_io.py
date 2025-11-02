from datetime import datetime
import json
import uuid
from modules.alerts import check_for_decline

# =========================================
# MODULE: Save Data with Timestamp & Alerts
# =========================================
def save_data(data, metrics, filename="health_history.json"):
    """Save user data and calculated metrics to JSON history file."""

    record = {
        'data': data,
        'metrics': metrics,
        'timestamp': datetime.now().isoformat()
    }

    try:
        with open(filename, 'r') as f:
            all_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_data = []

    all_data.append(record)

    with open(filename, 'w') as f:
        json.dump(all_data, f, indent=4)

    print(f"\n✅ Data successfully saved to {filename} at {record['timestamp']}.")
    
    # Check for any declining trends
    check_for_decline(filename)

