import time
import json
import hmac
import hashlib
import requests
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class MarketDataManager:
    """Custom CoinDCX Market Data Manager (no CCXT dependency for CoinDCX)"""

    def __init__(self):
        """Initialize CoinDCX connection using official API style."""
        from config import COINDCX_API_KEY, COINDCX_API_SECRET  # Import from your config

        self.api_key = COINDCX_API_KEY
        self.api_secret = COINDCX_API_SECRET
        self.base_url = "https://api.coindcx.com"          # Main API endpoint
        self.public_url = "https://public.coindcx.com"     # For public market data

        if not self.api_key or not self.api_secret:
            logger.warning("⚠️ CoinDCX API keys not found in .env - running in limited mode")

        logger.info("✅ CoinDCX MarketDataManager initialized (custom integration)")

    def _sign_request(self, body: Dict) -> str:
        """Generate HMAC-SHA256 signature for private endpoints."""
        if not self.api_secret:
            return ""
        json_body = json.dumps(body, separators=(',', ':'))
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            json_body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def get_ticker(self, pair: str) -> Dict:
        """Get latest ticker for a pair (public endpoint)."""
        try:
            # Example: BTC_USDT → B-BTC_USDT (CoinDCX format)
            instrument = f"B-{pair.replace('_', '_')}" if '_' in pair else pair
            url = f"{self.public_url}/market_data/v3/ticker/{instrument}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                'last': float(data.get('lastPrice', 0)),
                'bid': float(data.get('bid', 0)),
                'ask': float(data.get('ask', 0)),
                'volume': float(data.get('volume', 0)),
                'timestamp': data.get('timestamp')
            }
        except Exception as e:
            logger.error(f"Failed to get ticker for {pair}: {e}")
            return {'last': 0, 'bid': 0, 'ask': 0}

    def get_candles(self, pair: str, interval: str = "1m", limit: int = 100) -> List[Dict]:
        """Get historical candles (public)."""
        try:
            params = {
                "pair": f"B-{pair.replace('_', '_')}",
                "interval": interval,
                "limit": limit
            }
            url = f"{self.public_url}/market_data/candlesticks"
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get candles for {pair}: {e}")
            return []

    # Add more methods as needed (place_order, get_balance, etc.)
    def place_order(self, side: str, pair: str, quantity: float, price: Optional[float] = None, order_type: str = "market"):
        """Example placeholder for order placement (expand as needed)."""
        timestamp = int(time.time() * 1000)
        body = {
            "timestamp": timestamp,
            "side": side.lower(),
            "pair": f"B-{pair.replace('_', '_')}",
            "order_type": order_type,
            "total_quantity": quantity,
        }
        if price and order_type != "market":
            body["price_per_unit"] = price

        signature = self._sign_request(body)

        headers = {
            "Content-Type": "application/json",
            "X-AUTH-APIKEY": self.api_key,
            "X-AUTH-SIGNATURE": signature
        }

        try:
            response = requests.post(f"{self.base_url}/exchange/v1/orders/create", 
                                   json=body, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ Order placed: {side} {quantity} {pair}")
            return response.json()
        except Exception as e:
            logger.error(f"❌ Order failed: {e}")
            return None
