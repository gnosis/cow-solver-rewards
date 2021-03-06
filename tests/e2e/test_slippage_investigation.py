import unittest
from datetime import datetime
from pprint import pprint

from duneapi.api import DuneAPI
from duneapi.types import DuneQuery, QueryParameter, Network

from src.fetch.period_slippage import QueryType, slippage_query


class TestDuneAnalytics(unittest.TestCase):
    def test_no_outrageous_slippage(self):
        """
        If numbers do not seem correct, the following script allows us to investigate
        which tx are having high slippage values in dollar terms
        """
        dune = DuneAPI.new_from_environment()
        period_start = datetime.strptime("2022-03-10", "%Y-%m-%d")
        period_end = datetime.strptime("2022-03-11", "%Y-%m-%d")
        slippage_per_tx = dune.fetch(
            DuneQuery.from_environment(
                raw_sql=slippage_query(QueryType.PER_TX),
                network=Network.MAINNET,
                name="Slippage Accounting",
                parameters=[
                    QueryParameter.date_type("StartTime", period_start),
                    QueryParameter.date_type("EndTime", period_end),
                    QueryParameter.text_type("TxHash", "0x"),
                ],
            )
        )
        slippage_per_tx.sort(key=lambda t: int(t["eth_slippage_wei"]))

        top_five_negative = slippage_per_tx[:5]
        top_five_positive = slippage_per_tx[-5:]

        pprint(top_five_negative + top_five_positive)
        for obj in top_five_negative + top_five_positive:
            assert abs(obj["eth_slippage_wei"]) < 1 * 10**18


if __name__ == "__main__":
    unittest.main()
