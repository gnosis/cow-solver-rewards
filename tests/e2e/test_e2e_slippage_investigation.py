import unittest
from unittest.mock import MagicMock, Mock
from datetime import datetime


from src.dune_analytics import DuneAnalytics, QueryParameter
from src.models import Network


def get_slippage_accounting(
        query_str: str,
        dune: DuneAnalytics,
        period_start: datetime,
        period_end: datetime
) -> list:
    data_set = dune.fetch(
        query_str,
        network=Network.MAINNET,
        name='Slippage Accounting',
        parameters=[
            QueryParameter.date_type("StartTime", period_start),
            QueryParameter.date_type("EndTime", period_end),
            QueryParameter.text_type('TxHash', '0x'),
        ])
    return data_set


class TestDuneAnalytics(unittest.TestCase):
    def test_no_solver_has_huge_slippage_values(self):
        '''
            If numbers do not seem correct, the following script allows to investigate 
            which tx are having high slippage values in dollar terms
        '''
        dune_connection = DuneAnalytics.new_from_environment()

        query_str = dune_connection.open_query("./queries/slippage/internal_token_transfers_for_settlements.sql") + "," + \
            dune_connection.open_query(
                "./queries/slippage/evaluate_slippage_from_internal_token_transfers_per_tx.sql")
        slippage_accounting = get_slippage_accounting(
            dune=dune_connection,
            query_str=query_str,
            period_start=datetime.strptime('2022-03-10', "%Y-%m-%d"),
            period_end=datetime.strptime('2022-03-11', "%Y-%m-%d"),
        )
        print(slippage_accounting)


if __name__ == '__main__':
    unittest.main()