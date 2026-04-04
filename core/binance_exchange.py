"""Binance Exchange Integration for IndiaCryptoAlpha"""

import os
import time
import hmac
import hashlib
import requests
import logging
from typing import Dict, List, Optional
import pandas as pd
from .exchange_base import BaseExchange

logger = logging.getLogger(__name__)


class BinanceExchange(BaseExchange):
    """Binance Exchange implementation using Binance REST API"""

    def __init__(self, api_key: str = "", api_secret: str = "", **kwargs):
        super().__init__(api_key, api_secret, **kwargs)
        self.base_url = "https://api.binance.com"

    def _sign_request(self, params: Dict) -> Dict:
        """Sign Binance API request with HMAC-SHA256"""
        if not self.api_secret:
            return params
        query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def get_ticker(self, symbol: str) -> Dict:
        """Get latest ticker for a symbol (Binance uses BTCUSDT format)"""
        try:
            # Convert symbol to Binance format (remove hyphen, convert INR to USDT)
            binance_symbol = symbol.replace("-", "").replace("INR", "USDT")
            url = f"{self.base_url}/api/v3/ticker/bookTicker"
            params = {"symbol": binance_symbol}
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if "bidPrice" in data and "askPrice" in data:
                    return {
                        "last": float(
                            data.get(
                                "lastPrice",
                                (float(data["bidPrice"]) + float(data["askPrice"])) / 2,
                            )
                        ),
                        "bid": float(data["bidPrice"]),
                        "ask": float(data["askPrice"]),
                        "volume": float(data.get("volume", 0)),
                        "timestamp": int(time.time() * 1000),
                    }

            # Fallback to price ticker
            url = f"{self.base_url}/api/v3/ticker/price"
            response = requests.get(url, params={"symbol": binance_symbol}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                price = float(data["price"])
                return {
                    "last": price,
                    "bid": price * 0.999,
                    "ask": price * 1.001,
                    "volume": 0,
                    "timestamp": int(time.time() * 1000),
                }

        except Exception as e:
            logger.error(f"Binance ticker error for {symbol}: {e}")
        return {
            "last": 0,
            "bid": 0,
            "ask": 0,
            "volume": 0,
            "timestamp": int(time.time() * 1000),
        }

    def get_candles(
        self, symbol: str, interval: str = "1m", limit: int = 100
    ) -> List[Dict]:
        """Get historical OHLCV candles from Binance"""
        try:
            binance_symbol = symbol.replace("-", "").replace("INR", "USDT")
            url = f"{self.base_url}/api/v3/klines"
            params = {"symbol": binance_symbol, "interval": interval, "limit": limit}
            response = requests.get(url, params=params, timeout=15)

            if response.status_code == 200:
                klines = response.json()
                candles = []
                for k in klines:
                    candles.append(
                        {
                            "time": k[0],
                            "open": float(k[1]),
                            "high": float(k[2]),
                            "low": float(k[3]),
                            "close": float(k[4]),
                            "volume": float(k[5]),
                        }
                    )
                return candles
        except Exception as e:
            logger.error(f"Binance candles error for {symbol}: {e}")
        return []

    def place_order(
        self,
        side: str,
        symbol: str,
        quantity: float,
        price: Optional[float] = None,
        order_type: str = "market",
    ) -> Optional[Dict]:
        """Place order on Binance"""
        try:
            binance_symbol = symbol.replace("-", "").replace("INR", "USDT")
            timestamp = int(time.time() * 1000)
            params = {
                "symbol": binance_symbol,
                "side": side.upper(),
                "type": order_type.upper(),
                "quantity": quantity,
                "timestamp": timestamp,
            }

            if order_type != "market" and price:
                params["price"] = price
                params["type"] = "LIMIT"
                params["timeInForce"] = "GTC"

            params = self._sign_request(params)
            headers = {"X-MBX-APIKEY": self.api_key} if self.api_key else {}

            response = requests.post(
                f"{self.base_url}/api/v3/order",
                params=params,
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    f"Binance order error: {response.status_code} - {response.text}"
                )
        except Exception as e:
            logger.error(f"Binance order exception: {e}")
        return None

    def get_balance(self) -> Dict:
        """Get Binance account balance"""
        try:
            timestamp = int(time.time() * 1000)
            params = {"timestamp": timestamp}
            params = self._sign_request(params)
            headers = {"X-MBX-APIKEY": self.api_key} if self.api_key else {}

            response = requests.get(
                f"{self.base_url}/api/v3/account",
                params=params,
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                balances = {}
                for asset in data.get("balances", []):
                    free = float(asset["free"])
                    locked = float(asset["locked"])
                    if free > 0 or locked > 0:
                        balances[asset["asset"]] = {
                            "free": free,
                            "locked": locked,
                            "total": free + locked,
                        }
                return balances
        except Exception as e:
            logger.error(f"Binance balance error: {e}")
        return {}

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get open orders from Binance"""
        try:
            timestamp = int(time.time() * 1000)
            params = {"timestamp": timestamp}

            if symbol:
                params["symbol"] = symbol.replace("-", "").replace("INR", "USDT")

            params = self._sign_request(params)
            headers = {"X-MBX-APIKEY": self.api_key} if self.api_key else {}

            response = requests.get(
                f"{self.base_url}/api/v3/openOrders",
                params=params,
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Binance open orders error: {e}")
        return []
