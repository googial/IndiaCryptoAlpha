"""CoinDCX Exchange Integration for IndiaCryptoAlpha"""

import os
import time
import json
import hmac
import hashlib
import requests
import logging
from typing import Dict, List, Optional
import pandas as pd
from .exchange_base import BaseExchange

logger = logging.getLogger(__name__)


class CoinDCXExchange(BaseExchange):
    """CoinDCX Exchange implementation using CoinDCX REST API"""

    def __init__(self, api_key: str = "", api_secret: str = "", **kwargs):
        super().__init__(api_key, api_secret, **kwargs)
        self.base_url = "https://api.coindcx.com"
        self.public_url = "https://api.coindcx.com"

    def _sign_request(self, body: Dict) -> str:
        """Generate HMAC-SHA256 signature for CoinDCX private endpoints."""
        if not self.api_secret:
            return ""
        json_body = json.dumps(body, separators=(",", ":"))
        signature = hmac.new(
            self.api_secret.encode("utf-8"), json_body.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return signature

    def get_ticker(self, symbol: str) -> Dict:
        """Get latest ticker for a pair (public endpoint)."""
        try:
            # CoinDCX public ticker endpoint
            url = f"{self.public_url}/exchange/ticker"
            params = {"pair": symbol}
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and data.get("last_price"):
                    return {
                        "last": float(data["last_price"]),
                        "bid": float(data.get("bid", 0)),
                        "ask": float(data.get("ask", 0)),
                        "volume": float(data.get("volume", 0)),
                        "timestamp": data.get("timestamp", int(time.time() * 1000)),
                    }

            logger.warning(
                f"Ticker API returned status {response.status_code}, using mock data"
            )
            return self._get_mock_ticker(symbol)
        except Exception as e:
            logger.warning(f"Failed to get ticker for {symbol}: {e}, using mock data")
            return self._get_mock_ticker(symbol)

    def _get_mock_ticker(self, symbol: str) -> Dict:
        """Generate mock ticker data for demo purposes."""
        import random

        base_prices = {
            "BTC-INR": 3500000,
            "ETH-INR": 250000,
            "XRP-INR": 150,
            "ADA-INR": 50,
            "SOL-INR": 8000,
            "DOGE-INR": 25,
        }
        base = base_prices.get(symbol, 1000)
        last = base + random.uniform(-base * 0.01, base * 0.01)
        return {
            "last": round(last, 2),
            "bid": round(last * 0.999, 2),
            "ask": round(last * 1.001, 2),
            "volume": random.uniform(100, 10000),
            "timestamp": int(time.time() * 1000),
        }

    def get_candles(
        self, symbol: str, interval: str = "1m", limit: int = 100
    ) -> List[Dict]:
        """Get historical candles (public)."""
        try:
            # CoinDCX v1 candlesticks
            url = f"{self.public_url}/exchange/v1/candlesticks"
            params = {"pair": symbol, "interval": interval, "limit": limit}
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(
                    f"Candles API returned status {response.status_code}, using mock data"
                )
                return self._get_mock_candles(symbol, interval, limit)
        except Exception as e:
            logger.warning(f"Failed to get candles for {symbol}: {e}, using mock data")
            return self._get_mock_candles(symbol, interval, limit)

    def _get_mock_candles(self, symbol: str, interval: str, limit: int) -> List[Dict]:
        """Generate mock OHLCV candles."""
        import random

        base_prices = {
            "BTC-INR": 3500000,
            "ETH-INR": 250000,
            "XRP-INR": 150,
            "ADA-INR": 50,
            "SOL-INR": 8000,
            "DOGE-INR": 25,
        }
        base = base_prices.get(symbol, 1000)
        now = int(time.time() * 1000)
        interval_ms = {
            "1m": 60 * 1000,
            "5m": 5 * 60 * 1000,
            "15m": 15 * 60 * 1000,
            "1h": 60 * 60 * 1000,
            "4h": 4 * 60 * 60 * 1000,
            "1d": 24 * 60 * 60 * 1000,
        }.get(interval, 60 * 1000)
        candles = []
        current_time = now - (limit * interval_ms)
        price = base
        for i in range(limit):
            open_price = price + random.uniform(-price * 0.002, price * 0.002)
            close_price = open_price + random.uniform(-price * 0.005, price * 0.005)
            high_price = max(open_price, close_price) + random.uniform(0, price * 0.003)
            low_price = min(open_price, close_price) - random.uniform(0, price * 0.003)
            volume = (
                random.uniform(1, 100)
                if symbol in ["BTC-INR", "ETH-INR"]
                else random.uniform(100, 10000)
            )
            candle = {
                "time": current_time,
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": round(volume, 2),
            }
            candles.append(candle)
            price = close_price
            current_time += interval_ms
        return candles

    def place_order(
        self,
        side: str,
        symbol: str,
        quantity: float,
        price: Optional[float] = None,
        order_type: str = "market",
    ) -> Optional[Dict]:
        """Place order on CoinDCX"""
        if not self.api_key:
            logger.warning(
                "⚠️ Cannot place order: API key not configured (paper trading)"
            )
            return None
        timestamp = int(time.time() * 1000)
        body = {
            "timestamp": timestamp,
            "side": side.lower(),
            "pair": symbol,
            "order_type": order_type,
            "total_quantity": quantity,
        }
        if price and order_type != "market":
            body["price_per_unit"] = price
        signature = self._sign_request(body)
        headers = {
            "Content-Type": "application/json",
            "X-AUTH-APIKEY": self.api_key,
            "X-AUTH-SIGNATURE": signature,
        }
        try:
            response = requests.post(
                f"{self.base_url}/exchange/v1/orders/create",
                json=body,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            logger.info(f"✅ Order placed: {side} {quantity} {symbol}")
            return response.json()
        except Exception as e:
            logger.error(f"❌ Order failed: {e}")
            return None

    def get_balance(self) -> Dict:
        """Get CoinDCX account balance (simplified - uses mock if no API key)"""
        # CoinDCX balance endpoint would go here; for now return empty
        if not self.api_key:
            logger.warning("No API key — returning empty balance")
            return {}
        try:
            timestamp = int(time.time() * 1000)
            body = {"timestamp": timestamp}
            signature = self._sign_request(body)
            headers = {
                "Content-Type": "application/json",
                "X-AUTH-APIKEY": self.api_key,
                "X-AUTH-SIGNATURE": signature,
            }
            response = requests.get(
                f"{self.base_url}/exchange/v1/users/balances",
                headers=headers,
                timeout=10,
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"CoinDCX balance error: {e}")
        return {}

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders from CoinDCX"""
        if not self.api_key:
            return []
        try:
            timestamp = int(time.time() * 1000)
            body = {"timestamp": timestamp}
            if symbol:
                body["pair"] = symbol
            signature = self._sign_request(body)
            headers = {
                "Content-Type": "application/json",
                "X-AUTH-APIKEY": self.api_key,
                "X-AUTH-SIGNATURE": signature,
            }
            response = requests.get(
                f"{self.base_url}/exchange/v1/orders/open",
                headers=headers,
                json=body,
                timeout=10,
            )
            if response.status_code == 200:
                return response.json().get("data", [])
        except Exception as e:
            logger.error(f"CoinDCX open orders error: {e}")
        return []
