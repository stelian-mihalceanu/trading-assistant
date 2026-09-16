# Trading Assistant

Minimal cross-platform mobile trading research app.

## Stack

- Mobile: Expo + React Native + TypeScript
- Backend: FastAPI + Python
- Market data: yfinance
- Technical analysis: pandas / numpy

The old Streamlit UI has been removed. The mobile app is the product UI; the Python code is used as a small API/backend.

## Mobile MVP

The first version intentionally stays small:

- ticker search
- latest price and daily change
- SMA 20 / 50 / 200
- RSI and ATR
- explainable analysis signal
- optional position-size reference from the API

No broker execution and no real-money trading are included.

## Run the API

```bash
python -m pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 8000
```

## Run the mobile app

```bash
cd mobile
npm install
npm start
```

For a physical device, set the API URL before starting the app:

```bash
EXPO_PUBLIC_API_URL=http://YOUR-LAN-IP:8000 npm start
```

## Build

Expo's current stable SDK is used for the mobile project. The same React Native project targets iOS and Android/Fire OS; native store packaging is handled separately for Apple App Store and Amazon Appstore.
