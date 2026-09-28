# API Demo Traffic Generator

Small Python utility for generating spaced-out HTTP traffic against a demo API server.

## Setup

```bash
python -m pip install requests
```

## Run

```bash
python api_traffic_generator.py
```

Point it at another demo server:

```bash
BASE_URL=https://api.example.com python api_traffic_generator.py
```

Tune request spacing and number of rounds:

```bash
MIN_DELAY_SECONDS=2 MAX_DELAY_SECONDS=10 ROUNDS=5 python api_traffic_generator.py
```

## Customize

Edit the `REQUESTS` list in `api_traffic_generator.py` to match the routes, methods, and JSON payloads exposed by your demo API.

Authentication headers can be added to the `HEADERS` dictionary. Avoid committing real API keys or tokens.
