import unittest
from src.fetch.period_slippage import generate_sql_query_for_allowed_token_list


class TestQueryBuilding(unittest.TestCase):

    def test_builds_intended_query(self):
        list = ['0xde1c59bc25d806ad9ddcbe246c4b5e5505645718']
        expected_query = "allow_listed_tokens as ( Select * from (VALUES('\\xde1c59bc25d806ad9ddcbe246c4b5e5505645718' :: bytea)) AS t (token)),"
        query = generate_sql_query_for_allowed_token_list(list)
        self.assertEqual(query, expected_query)


if __name__ == '__main__':
    unittest.main()
