# ZeroApiWrapper

**Unofficial Zerodha Kite API — no subscription required.**

ZeroApiWrapper is a lightweight Python client for the Zerodha Kite platform that authenticates directly through the web login flow instead of the official Kite Connect API. No paid API subscription, no API key, no API secret — just your Zerodha credentials and a TOTP seed.

## How it works

The standard Kite Connect API requires a paid subscription and OAuth token generation. This library bypasses all of that by replicating the web login flow — credentials + TOTP — to obtain an `enctoken`, which is then used to sign all subsequent requests. Think of it as scripting Kite web from Python.

> **⚠️ Not affiliated with Zerodha. Use at your own risk — this goes against Zerodha's ToS.**

## Features

| Feature | Supported |
|---|---|
| Place / Modify / Cancel orders | ✅ |
| GTT (bracket/cover) orders | ✅ |
| Historical data (any interval) | ✅ |
| Live instrument list | ✅ |
| Portfolio & positions | ✅ |
| Margin & profile info | ✅ |
| All exchanges (NSE, BSE, NFO, CDS, BFO, MCX) | ✅ |
| All product types (MIS, CNC, NRML, CO) | ✅ |
| All order types (MARKET, LIMIT, SL, SL-M) | ✅ |
| AMO (After Market Orders) | ✅ |

## Quick start

```bash
pip install requests python-dateutil pyotp python-dotenv
```

Create a `.env` file:

```
ZERODHA_USER_ID=AB1234
ZERODHA_PASSWORD=your_password
ZERODHA_2FA=ASDFG678FGHJK234VBNM789VBNM
```

```python
from zero import KiteApp

kite = KiteApp()

# Fetch profile
print(kite.profile())

# Get positions
print(kite.positions())

# Place a market order
kite.place_order(
    variety=KiteApp.VARIETY_REGULAR,
    exchange=KiteApp.EXCHANGE_NSE,
    tradingsymbol="RELIANCE",
    transaction_type=KiteApp.TRANSACTION_TYPE_BUY,
    quantity=1,
    product=KiteApp.PRODUCT_MIS,
    order_type=KiteApp.ORDER_TYPE_MARKET,
)

# Fetch historical data
data = kite.historical_data(
    instrument_token=738561,
    from_date="2025-01-01",
    to_date="2025-12-31",
    interval=KiteApp.TIMEFRAME_1DAY,
)
```

## API Reference

### Authentication

| Method | Description |
|---|---|
| `login()` | Authenticates via web flow, stores `enctoken` in session |
| `isAuthenticated()` | Checks profile, re-logs in if token expired |

### Orders

| Method | Description |
|---|---|
| `place_order(variety, exchange, tradingsymbol, ...)` | Place a new order |
| `modify_order(variety, order_id, ...)` | Modify an existing order |
| `cancel_order(variety, order_id)` | Cancel an open order |
| `orders()` | List all orders for the day |

### GTT (Good Till Triggered)

| Method | Description |
|---|---|
| `gtt_orders()` | List all GTT triggers |
| `gtt_order(order_id)` | Get a specific GTT trigger |
| `gtt_create_order(...)` | Create a GTT order (OCO or single) |
| `gtt_delete_order(order_id)` | Delete a GTT trigger |

### Portfolio

| Method | Description |
|---|---|
| `positions()` | Current day positions |
| `margins()` | Available margins |
| `profile()` | User profile |

### Market Data

| Method | Description |
|---|---|
| `instruments(exchange=None)` | Full instrument list, optionally filtered by exchange |
| `historical_data(instrument_token, from_date, to_date, interval)` | OHLCV candles |

### Constants

The class exposes all Kite enum values as class attributes:

- **Timeframes**: `TIMEFRAME_1MIN`, `TIMEFRAME_3MIN`, `TIMEFRAME_5MIN`, `TIMEFRAME_10MIN`, `TIMEFRAME_15MIN`, `TIMEFRAME_30MIN`, `TIMEFRAME_1HOUR`, `TIMEFRAME_1DAY`, `TIMEFRAME_1WEEK`
- **Products**: `PRODUCT_MIS`, `PRODUCT_CNC`, `PRODUCT_NRML`, `PRODUCT_CO`
- **Order types**: `ORDER_TYPE_MARKET`, `ORDER_TYPE_LIMIT`, `ORDER_TYPE_SLM`, `ORDER_TYPE_SL`
- **Varieties**: `VARIETY_REGULAR`, `VARIETY_CO`, `VARIETY_AMO`
- **Transaction types**: `TRANSACTION_TYPE_BUY`, `TRANSACTION_TYPE_SELL`
- **Validity**: `VALIDITY_DAY`, `VALIDITY_IOC`
- **Exchanges**: `EXCHANGE_NSE`, `EXCHANGE_BSE`, `EXCHANGE_NFO`, `EXCHANGE_CDS`, `EXCHANGE_BFO`, `EXCHANGE_MCX`
- **GTT types**: `GTT_TYPE_OCO`, `GTT_TYPE_SINGLE`

## Important notes

- The session token (`enctoken`) is short-lived and auto-renews via `isAuthenticated()`.
- The `.env` file keeps your credentials out of source control.
- This is **not** the official Kite Connect API. Expect no guarantees on uptime or compatibility.
