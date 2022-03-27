import unittest

from src.cow_api import CowApi, OrderKind, QuoteRequest
from src.models import Address, AppData, Network


class TestCowApi(unittest.TestCase):
    def test_quote(self):
        cow = CowApi.for_network(Network.MAINNET)
        response = cow.quote(QuoteRequest(
            sell_token=Address("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"),
            buy_token=Address("0x6810e776880c02933d47db1b9fc05908e5386b96"),
            valid_to=0xffffffff,
            app_data=AppData.random(),
            kind=OrderKind.SELL,
            from_=Address("0x0000000000000000000000000000000000000000"),
            sell_amount_before_fee=10**18,
        ))
        self.assertEqual(response.quote.sell_amount + response.quote.fee_amount, 10**18)


if __name__ == "__main__":
    unittest.main()
