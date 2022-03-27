import unittest
from datetime import datetime
import json

from src.cow_api import CowApi, OrderKind, QuoteRequest, QuoteResponse, Quote, TokenBalance
from src.models import Address, AppData, Network


class TestCowApi(unittest.TestCase):
    def test_default_base_url(self):
        cow = CowApi.for_network(Network.MAINNET)
        self.assertEqual(cow.url, "https://api.cow.fi/mainnet")


class TestQuoteRequest(unittest.TestCase):
    def test_json_serialization(self):
        quote = QuoteRequest(
            sell_token=Address("0x1111111111111111111111111111111111111111"),
            buy_token=Address("0x2222222222222222222222222222222222222222"),
            receiver=Address("0x3333333333333333333333333333333333333333"),
            valid_to=42,
            kind=OrderKind.SELL,
            from_=Address("0x4444444444444444444444444444444444444444"),
            sell_amount_after_fee=10**18,
        )
        self.assertEqual(quote.to_json(), {
            "appData": "0x0000000000000000000000000000000000000000000000000000000000000000",
            "buyToken": "0x2222222222222222222222222222222222222222",
            "buyTokenBalance": "erc20",
            "from": "0x4444444444444444444444444444444444444444",
            "kind": "sell",
            "partiallyFillable": False,
            "receiver": "0x3333333333333333333333333333333333333333",
            "sellAmountAfterFee": "1000000000000000000",
            "sellToken": "0x1111111111111111111111111111111111111111",
            "sellTokenBalance": "erc20",
            "validTo": 42
        })

    def test_json_serialization_errors(self):
        def empty_quote() -> QuoteRequest:
            return QuoteRequest(
                Address.zero(),
                Address.zero(),
                Address.zero(),
                0,
                OrderKind.SELL,
            )

        # missing amounts
        with self.assertRaises(ValueError):
            q = empty_quote()
            q.to_json()
        # duplicate amounts
        with self.assertRaises(ValueError):
            q = empty_quote()
            q.sell_amount_after_fee = 0
            q.sell_amount_before_fee = 0
            q.to_json()
        # buy amount for sell order
        with self.assertRaises(ValueError):
            q = empty_quote()
            q.kind = OrderKind.SELL
            q.buy_amount_after_fee = 0
            q.to_json()
        # sell amount for buy order
        with self.assertRaises(ValueError):
            q = empty_quote()
            q.kind = OrderKind.BUY
            q.sell_amount_before_fee = 0
            print(q.to_json())


class TestQuoteResponse(unittest.TestCase):
    def test_json_serialization(self):
        quote = """{
            "quote": {
                "sellToken": "0x1111111111111111111111111111111111111111",
                "buyToken": "0x2222222222222222222222222222222222222222",
                "receiver": "0x3333333333333333333333333333333333333333",
                "sellAmount": "123",
                "buyAmount": "456",
                "validTo": 7,
                "appData": "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "feeAmount": "789",
                "kind": "buy",
                "partiallyFillable": true,
                "sellTokenBalance": "external",
                "buyTokenBalance": "erc20"
            },
            "from": "0x4444444444444444444444444444444444444444",
            "expiration": "2022-03-27T16:29:48.650107010Z",
            "extraField": "that gets ignored"
        }"""
        self.assertEqual(QuoteResponse.from_json(json.loads(quote)), QuoteResponse(
            quote = Quote(
                sell_token = Address("0x1111111111111111111111111111111111111111"),
                buy_token = Address("0x2222222222222222222222222222222222222222"),
                receiver = Address("0x3333333333333333333333333333333333333333"),
                sell_amount = 123,
                buy_amount = 456,
                valid_to = 7,
                app_data = AppData("0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"),
                fee_amount = 789,
                kind = OrderKind.BUY,
                partially_fillable = True,
                sell_token_balance = TokenBalance.EXTERNAL,
                buy_token_balance = TokenBalance.ERC20,
            ),
            from_ = Address("0x4444444444444444444444444444444444444444"),
            expiration = datetime.fromisoformat("2022-03-27T16:29:48.650107"),
        ))


if __name__ == "__main__":
    unittest.main()
