# health_check.py
"""
A simple health check script for Docker HEALTHCHECK directive.
Checks if the model service responds with status 200 under a latency threshold.
"""

import requests
import sys
import time

def check_model_health():
    start = time.time()
    try:
        resp = requests.get("http://localhost:8080/health", timeout=5)
        lat = time.time()-start
        if resp.status_code==200 and lat<=0.5:
            return True
    except requests.RequestException:
        pass
    return False

if __name__ == "__main__":
    if check_model_health():
        sys.exit(0)
    else:
        sys.exit(1)
