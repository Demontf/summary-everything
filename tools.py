from datetime import datetime, timedelta
import json


def save_obj_json(obj, filename):
    with open(filename, 'w') as f:
        json.dump(obj, f)
        f.close()


def get_date_x_days_ago(x):
    now = datetime.now()
    x_days_ago = now - timedelta(days=x)
    return x_days_ago.strftime('%Y-%m-%d')


def split_array(arr, chunk=25):
    return [arr[i:i + chunk] for i in range(0, len(arr), chunk)]
