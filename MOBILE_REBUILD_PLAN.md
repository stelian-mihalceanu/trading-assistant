# Trading Assistant — Native Mobile Rebuild

## Goal
Replace the Streamlit UI with a production mobile application targeting iOS and an Android/Fire OS build for Amazon Appstore.

## Important distribution constraint
Apple App Store and Amazon Appstore are different targets. The Apple target is a native iOS app. Amazon Appstore targets Fire OS/Android, so the shared application layer should be cross-platform rather than iOS-only.

## Proposed stack
- React Native + Expo prebuild / native iOS and Android projects
- TypeScript
- React Navigation
- TanStack Query for API/server state
- Zustand for lightweight local app state
- Native secure storage for auth tokens
- FastAPI backend retained/refactored as the market-data and analysis API
- Python analytics modules retained on the server; no Streamlit runtime
- PostgreSQL later for user accounts, watchlists, alerts and subscriptions if backend persistence is added

## Mobile product
1. Home dashboard: watchlist, market status, latest prices and daily moves.
2. Symbol search with exchange-aware ticker normalization.
3. Asset detail: price chart, OHLC, SMA/EMA, RSI, MACD, Bollinger Bands, ATR, volume.
4. Research summary: transparent factor breakdown and signal explanations.
5. Company view: market cap, valuation, fundamentals, analyst consensus where available.
6. Risk tools: position sizing, stop/target scenarios and reward/risk calculations.
7. Watchlists: add/remove symbols and sort by move.
8. Alerts: price threshold and signal-condition alerts backed by server scheduling/push notifications.
9. Portfolio/paper trading: positions, P&L, transactions and history; explicitly paper-only unless a separately licensed broker integration is added.
10. Settings: data refresh, notifications, privacy, legal/disclosure pages.

## API changes
- GET /health
- GET /api/v1/assets/{ticker}/quote
- GET /api/v1/assets/{ticker}/history?period=1y&interval=1d
- GET /api/v1/assets/{ticker}/analysis
- GET /api/v1/assets/{ticker}/fundamentals
- GET /api/v1/assets/{ticker}/analysts
- POST/GET/DELETE /api/v1/watchlists
- POST/GET/DELETE /api/v1/alerts
- POST/GET /api/v1/paper/positions
- GET /api/v1/paper/performance

Responses should be versioned, typed, stable, and mobile-friendly. API failures should not be collapsed into 500 for all exceptions; validation errors and upstream-data failures need distinct status codes and user-safe messages.

## Data provider direction
The current code uses yfinance directly from the application layer. This should move behind a provider interface so the mobile backend is not coupled to a single upstream implementation. Start with Yahoo/yfinance compatibility, then add a production market-data provider when needed.

## Security
- No market-data provider API keys in the mobile app.
- Secrets stay server-side.
- Short-lived access tokens plus refresh tokens if authentication is introduced.
- Secure token storage on device.
- Rate limiting and server-side input validation.
- Never claim real-time data unless the selected provider actually supplies real-time data.

## Store readiness
### Apple
The app must clearly disclose its educational/research nature and applicable financial-services limitations. Apps that facilitate financial trading/investing/money management are subject to Apple's review rules and may require the appropriate legal entity/licensing in supported locations.

### Amazon Appstore
Ship an Android/Fire OS variant. Fire OS is Android-based, but Google Play services are not universally available, so avoid hard dependencies on Google-only services. Where platform-specific services are required, use a compatible abstraction or Amazon equivalent.

## Migration approach
1. Freeze the current Streamlit UI as legacy.
2. Extract/refactor analytics into API-safe service modules.
3. Stabilize FastAPI contracts and tests.
4. Create mobile workspace with iOS/Android targets.
5. Implement Home/Search/Asset Detail/Research/Risk screens.
6. Add Watchlist, Alerts, Paper Portfolio.
7. Add push notifications and authentication.
8. Add CI for TypeScript, tests, Android build and iOS build validation.
9. Remove Streamlit/runtime files once mobile parity is reached.
10. Prepare store metadata, privacy policy, disclosures and release builds.
