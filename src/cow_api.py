"""
Utilities for internacting with the CowSwap API.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import re
from typing import Any, Optional

import requests

from src.models import Address, AppData, Network

DEFAULT_BASE_URL = "https://api.cow.fi"

class CowApi:
    """
    CowSwap orderbook API client.
    """

    def __init__(self, url: str):
        """
        Creates a new instance of the CowSwap API client.
        :param url: the API base URL
        """
        self.url = url

    @classmethod
    def for_network(cls, network: Network) -> CowApi:
        """
        Create a new instance of the CowSwap API client with the default base
        URL for the specified network.
        :param network: the network
        """
        network_name = None
        if network == Network.MAINNET:
            network_name = "mainnet"
        elif network == Network.GCHAIN:
            network_name = "xdai"
        else:
            raise ValueError(f"unsupported network {network}")
        return cls(f"{DEFAULT_BASE_URL}/{network_name}")

    def _url(self, path: str) -> str:
        return f"{self.url}/{path}"

    def quote(self, request: QuoteRequst) -> QuoteResponse:
        print(self._url("api/v1/quote"))
        response = requests.post(self._url("api/v1/quote"), json=request.to_json())
        return QuoteResponse.from_json(response.json())


class TokenBalance(Enum):
    """
    The kind of token balance to use for trading.
    """
    ERC20 = "erc20"
    EXTERNAL = "external"
    INTERNAL = "internal"


class OrderKind(Enum):
    """
    The kind of order.
    """
    SELL = "sell"
    BUY = "buy"


class PriceQuality(Enum):
    """
    The kind of order.
    """
    FAST = "fast"
    OPTIMAL = "optimal"


@dataclass
class QuoteRequest:
    """
    A CowSwap API quote request.
    """

    from_: Address
    sell_token: Address
    buy_token: Address
    valid_to: int
    kind: OrderKind

    sell_amount_before_fee: Optional[int] = None
    sell_amount_after_fee: Optional[int] = None
    buy_amount_after_fee: Optional[int] = None

    receiver: Optional[Address] = None
    app_data: AppData = AppData.zero()
    partially_fillable: bool = False
    sell_token_balance: TokenBalance = TokenBalance.ERC20
    buy_token_balance: TokenBalance = TokenBalance.ERC20
    price_quality: Optional[PriceQuality] = None

    def to_json(self) -> dict[str, Any]:
        """
        Converts a request instance to a dictionary for JSON serialization.
        """

        # Do some name re-naming. In the future, it may be easier use a library
        # for serialization like `marshmallow`.
        value = {
            "sellToken": self.sell_token.address,
            "buyToken": self.buy_token.address,
            "validTo": self.valid_to,
            "appData": self.app_data.value,
            "kind": self.kind.value,
            "partiallyFillable": self.partially_fillable,
            "sellTokenBalance": self.sell_token_balance.value,
            "buyTokenBalance": self.buy_token_balance.value,
            "from": self.from_.address,
        }
        if self.receiver is not None:
            value["receiver"] = self.receiver.address
        if self.price_quality is not None:
            value["priceQuality"] = self.price_quality.value
        if self.kind == OrderKind.SELL and self.sell_amount_before_fee is not None and self.sell_amount_after_fee is None and self.buy_amount_after_fee is None:
            value["sellAmountBeforeFee"] = str(self.sell_amount_before_fee)
        elif self.kind == OrderKind.SELL and self.sell_amount_before_fee is None and self.sell_amount_after_fee is not None and self.buy_amount_after_fee is None:
            value["sellAmountAfterFee"] = str(self.sell_amount_after_fee)
        elif self.kind == OrderKind.BUY and self.sell_amount_before_fee is None and self.sell_amount_after_fee is None and self.buy_amount_after_fee is not None:
            value["buyAmountAfterFee"] = str(self.buy_amount_after_fee)
        else:
            raise ValueError("must specify exactly one sell/buy amount matching order kind")

        return value


@dataclass
class Quote:
    """
    A quoted CowSwap order.
    """
    sell_token: Address
    buy_token: Address
    receiver: Optional[Address]
    sell_amount: int
    buy_amount: int
    valid_to: int
    app_data: AppData
    fee_amount: int
    kind: OrderKind
    partially_fillable: bool
    sell_token_balance: TokenBalance
    buy_token_balance: TokenBalance


@dataclass
class QuoteResponse:
    """
    A CowSwap quote response.
    """
    quote: Quote
    from_: Address
    expiration: datetime

    @classmethod
    def from_json(cls, value: dict[str, Any]) -> QuoteResponse:
        qvalue = value["quote"]
        return QuoteResponse(
            quote = Quote(
                sell_token = Address(qvalue["sellToken"]),
                buy_token = Address(qvalue["buyToken"]),
                receiver = None if qvalue["receiver"] is None else Address(qvalue["receiver"]),
                sell_amount = int(qvalue["sellAmount"]),
                buy_amount = int(qvalue["buyAmount"]),
                valid_to = int(qvalue["validTo"]),
                app_data = AppData(qvalue["appData"]),
                fee_amount = int(qvalue["feeAmount"]),
                kind = OrderKind(qvalue["kind"]),
                partially_fillable = bool(qvalue["partiallyFillable"]),
                sell_token_balance = TokenBalance(qvalue["sellTokenBalance"]),
                buy_token_balance = TokenBalance(qvalue["buyTokenBalance"]),
            ),
            from_ = Address(value["from"]),
            # The date time we get is not-quite-ISO format. Specifically, it has
            # 3 too many digits in the fractional part and uses Z to denote the
            # UTC timezone - strip this suffix to parse the datetime.
            expiration = datetime.fromisoformat(re.sub(r'\d\d\dZ$', "", value["expiration"]))
        )
