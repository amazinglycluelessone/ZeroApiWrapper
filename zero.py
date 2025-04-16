import os
try:
    import requests
except ImportError:
    os.system('python -m pip install requests')
try:
    import dateutil
except ImportError:
    os.system('python -m pip install python-dateutil')
try:
    import pyotp
except ImportError:
    os.system('python -m pip install pyotp')
try:
    from dotenv import load_dotenv
except ImportError:
    os.system('python -m pip install python-dotenv')
import json
import requests
import dateutil.parser
import requests
import dateutil
import pyotp
from dotenv import load_dotenv

load_dotenv()

class KiteApp:

    session = requests.Session()
    headers = {
        "accept": "application/json, text/plain, */*",
        "Accept-Encoding": "deflate",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-kite-version": "3.0.0",
        "referer": "https://kite.zerodha.com/",
    }


    # Timeframes
    TIMEFRAME_1MIN = "1minute"
    TIMEFRAME_3MIN = "3minute"
    TIMEFRAME_5MIN = "5minute"
    TIMEFRAME_10MIN = "10minute"
    TIMEFRAME_15MIN = "15minute"
    TIMEFRAME_30MIN = "30minute"
    TIMEFRAME_1HOUR = "60minute"
    TIMEFRAME_1DAY = "day"
    TIMEFRAME_1WEEK = "week"
    

    # Products
    PRODUCT_MIS = "MIS"
    PRODUCT_CNC = "CNC"
    PRODUCT_NRML = "NRML"
    PRODUCT_CO = "CO"

    # Order types
    ORDER_TYPE_MARKET = "MARKET"
    ORDER_TYPE_LIMIT = "LIMIT"
    ORDER_TYPE_SLM = "SL-M"
    ORDER_TYPE_SL = "SL"

    # Varities
    VARIETY_REGULAR = "regular"
    VARIETY_CO = "co"
    VARIETY_AMO = "amo"

    # Transaction type
    TRANSACTION_TYPE_BUY = "BUY"
    TRANSACTION_TYPE_SELL = "SELL"

    # Validity
    VALIDITY_DAY = "DAY"
    VALIDITY_IOC = "IOC"

    # Exchanges
    EXCHANGE_NSE = "NSE"
    EXCHANGE_BSE = "BSE"
    EXCHANGE_NFO = "NFO"
    EXCHANGE_CDS = "CDS"
    EXCHANGE_BFO = "BFO"
    EXCHANGE_MCX = "MCX"

    # GTT order type
    GTT_TYPE_OCO = "two-leg"
    GTT_TYPE_SINGLE = "single"    

    def __init__(self):
        self.root_url = "https://kite.zerodha.com/oms"
        self.login()
        

    def login(self):
        session = requests.Session()
        loginHeaders = self.headers.copy()
        loginHeaders["content-type"] = "application/x-www-form-urlencoded"
        
        response = session.post('https://kite.zerodha.com/api/login', headers=loginHeaders, data={
            "user_id": os.getenv("ZERODHA_USERID"),
            "password": os.getenv("ZERODHA_PASSWORD"),
            "type": "user_id"

        }, timeout=10)
        if response.status_code != 200:
            print("Invalid credentials!")
            return None
        else:
            response = session.post('https://kite.zerodha.com/api/twofa', data={
                "request_id": response.json()['data']['request_id'],
                "twofa_value": pyotp.TOTP(os.getenv('ZERODHA_2FA')).now(),
                "user_id": response.json()['data']['user_id']
            })
            if response.status_code != 200:
                print("Invalid 2FA code!")
                return None
            enctoken = response.cookies.get('enctoken')
            if enctoken:
                self.headers["Authorization"] = f"enctoken {enctoken}"
                self.headers["x-kite-userid"] = f"{os.getenv("ZERODHA_USERID")}"
                self.session.headers = self.headers
                return enctoken
            else:
                print("Enter valid details!")
                return None
    
    def isAuthenticated(self):
        if self.profile() is None:
            print('Generating a new token...')
            if self.login() is None:
                print("Unable to login!")
                return False
        return True

    def instruments(self, exchange=None):
        data = self.session.get(f"https://api.kite.trade/instruments").text.split("\n")
        Exchange = []
        for i in data[1:-1]:
            row = i.split(",")
            if exchange is None or exchange == row[11]:
                Exchange.append({'instrument_token': int(row[0]), 'exchange_token': row[1], 'tradingsymbol': row[2],
                                 'name': row[3][1:-1], 'last_price': float(row[4]),
                                 'expiry': dateutil.parser.parse(row[5]).date() if row[5] != "" else None,
                                 'strike': float(row[6]), 'tick_size': float(row[7]), 'lot_size': int(row[8]),
                                 'instrument_type': row[9], 'segment': row[10],
                                 'exchange': row[11]})
        return Exchange

    def historical_data(self, instrument_token, from_date, to_date, interval, continuous=False, oi=False):
        params = {"from": from_date,
                  "to": to_date,
                  "interval": interval,
                  "continuous": 1 if continuous else 0,
                  "oi": 1 if oi else 0}
        lst = self.session.get(
            f"{self.root_url}/instruments/historical/{instrument_token}/{interval}", params=params,
            headers=self.headers).json()["data"]["candles"]
        records = []
        for i in lst:
            record = {"date": dateutil.parser.parse(i[0]), "open": i[1], "high": i[2], "low": i[3],
                      "close": i[4], "volume": i[5],}
            if len(i) == 7:
                record["oi"] = i[6]
            records.append(record)
        return records

    def margins(self):
        response = self.session.get(f"{self.root_url}/user/margins", headers=self.headers).json()
        if response.status_code != 200:
            return None
        else:
            return response["data"]       
        

    def profile(self):
        response = self.session.get(f"{self.root_url}/user/profile", headers=self.headers).json()
        if response.status_code != 200:
            print("Token Expired!")
            return None
        else:   
            return response["data"]

    def orders(self):
        response = self.session.get(f"{self.root_url}/orders", headers=self.headers).json()
        if response.status_code != 200:
            return None
        else:
            return response["data"]
 
    def positions(self):
        response = self.session.get(f"{self.root_url}/portfolio/positions", headers=self.headers).json()
        if response.status_code != 200:
            return None
        else:
            return response["data"]
        
    # Get list of GTT orders from the current account
    def gtt_orders(self):
        response = self.session.get(f"{self.root_url}/gtt/triggers", headers=self.headers).json()
        if response.status_code != 200:
            return None
        else:
            return response["data"]

    # Get a specific GTT order based on orderId
    def gtt_order(self, order_id):
        response = self.session.get(f"{self.root_url}/gtt/triggers/{order_id}", headers=self.headers).json()
        if response.status_code != 200:
            return None
        else:
            return response["data"]
                
    # Delete a specific GTT order based on orderId
    def gtt_delete_order(self, order_id):
        response = self.session.delete(f"{self.root_url}/gtt/triggers/{order_id}", headers=self.headers).json()
        if response.status_code != 200:
            return None
        else:
            return response["data"]
        
    # Create a GTT order
    def gtt_create_order(self, exchange, tradingsymbol, transaction_type, order_type, product, trigger_type, last_price, quantity, price_values, trigger_values):
        assert trigger_type in [self.GTT_TYPE_OCO, self.GTT_TYPE_SINGLE]

        condition = {
            "exchange": exchange,
            "tradingsymbol": tradingsymbol,
            "trigger_values": trigger_values,
            "last_price": last_price,
        }        

        gtt_leg_orders = []
        for price in price_values:
            gtt_leg_orders.append({
                "exchange": exchange,
                "tradingsymbol": tradingsymbol,
                "transaction_type": transaction_type,
                "quantity": quantity,
                "price": price,
                "order_type": order_type,
                "product": product,
            })

        gtt_params = {
            "condition": json.dumps(condition),
            "orders": json.dumps(gtt_leg_orders), 
            "type": trigger_type, 
        }

        response = self.session.post(f"{self.root_url}/gtt/triggers", data=gtt_params, headers=self.headers).json()
        if response.status_code != 200:
            return None
        else:
            return response["data"]
    
    def place_order(self, variety, exchange, tradingsymbol, transaction_type, quantity, product, order_type, price=None,
                    validity=None, disclosed_quantity=None, trigger_price=None, squareoff=None, stoploss=None,
                    trailing_stoploss=None, tag=None):
        params = locals()
        del params["self"]
        for k in list(params.keys()):
            if params[k] is None:
                del params[k]
        response = self.session.post(f"{self.root_url}/orders/{variety}", data=params, headers=self.headers).json()
        if response.status_code != 200:
            return None
        else:
            return response["data"]["order_id"]
        
    def modify_order(self, variety, order_id, parent_order_id=None, quantity=None, price=None, order_type=None,
                     trigger_price=None, validity=None, disclosed_quantity=None):
        params = locals()
        del params["self"]
        for k in list(params.keys()):
            if params[k] is None:
                del params[k]

        response = self.session.put(f"{self.root_url}/orders/{variety}/{order_id}", data=params, headers=self.headers).json()
        if response.status_code != 200:
            return None
        else:
            return response["data"]["order_id"]
        
    def cancel_order(self, variety, order_id, parent_order_id=None):
        response = self.session.delete(f"{self.root_url}/orders/{variety}/{order_id}", data={"parent_order_id": parent_order_id} if parent_order_id else {}, headers=self.headers).json()
        if response.status_code != 200:
            return None
        else:
            return response["data"]["order_id"]