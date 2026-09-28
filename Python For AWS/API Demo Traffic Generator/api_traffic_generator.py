#!/usr/bin/env python3
"""
API Demo Traffic Generator

Generates low-rate, spaced-out HTTP requests against a demo API server.
Replace the example endpoints and payloads with your own demo routes.

Usage:
    python api_traffic_generator.py
    BASE_URL=https://api.example.com python api_traffic_generator.py
"""

import os
import random
import time
from datetime import datetime

import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
MIN_DELAY_SECONDS = float(os.getenv("MIN_DELAY_SECONDS", "3"))
MAX_DELAY_SECONDS = float(os.getenv("MAX_DELAY_SECONDS", "8"))
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
ROUNDS = int(os.getenv("ROUNDS", "3"))

# Add, remove, or modify requests here.
REQUESTS = [
    {"method": "GET", "path": "/health"},
    {"method": "GET", "path": "/api/products"},
    {"method": "GET", "path": "/api/users/1"},
    {
        "method": "POST",
        "path": "/api/search",
        "json": {"query": "demo"},
    },
    {
        "method": "POST",
        "path": "/api/orders",
        "json": {
            "product_id": 101,
            "quantity": 1,
            "source": "demo-traffic-generator",
        },
    },
]

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "api-demo-traffic-generator/1.0",
    "Content-Type": "application/json",
    # "Authorization": "Bearer REPLACE_ME",
}


def send_request(session: requests.Session, request_spec: dict) -> None:
    method = request_spec["method"].upper()
    url = f"{BASE_URL}{request_spec['path']}"

    try:
        response = session.request(
            method=method,
            url=url,
            headers=HEADERS,
            json=request_spec.get("json"),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{timestamp}] {method:<6} {request_spec['path']:<25} "
            f"-> HTTP {response.status_code} ({response.elapsed.total_seconds():.3f}s)"
        )

    except requests.RequestException as exc:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {method:<6} {request_spec['path']:<25} -> ERROR: {exc}")


def main() -> None:
    if MIN_DELAY_SECONDS < 0 or MAX_DELAY_SECONDS < MIN_DELAY_SECONDS:
        raise ValueError("Delay values are invalid.")

    print(f"Target: {BASE_URL}")
    print(
        f"Running {ROUNDS} round(s), with {MIN_DELAY_SECONDS}-"
        f"{MAX_DELAY_SECONDS}s between requests."
    )
    print("Press Ctrl+C to stop.\n")

    session = requests.Session()

    try:
        for round_number in range(1, ROUNDS + 1):
            print(f"--- Round {round_number}/{ROUNDS} ---")

            for index, request_spec in enumerate(REQUESTS):
                send_request(session, request_spec)

                is_last_request = (
                    round_number == ROUNDS and index == len(REQUESTS) - 1
                )
                if not is_last_request:
                    delay = random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
                    print(f"Waiting {delay:.1f}s...\n")
                    time.sleep(delay)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
