import argparse
from datetime import datetime
from pprint import pprint

from src.dune_analytics import DuneAnalytics, QueryParameter
from src.file_io import File
from src.models import Network
from src.token_list import HOSTED_ALLOWED_BUFFER_TRADING_TOKEN_LIST_URL, get_trusted_tokens_from_url


def generate_sql_query_for_allowed_token_list(token_list) -> str:
    query = "allow_listed_tokens as ( Select * from (VALUES"
    for address in token_list:
        query += f"('\{address[1:]}' :: bytea),"
    query = query[:-1]
    query += ") AS t (token)),"
    return query


def build_subquery(dune: DuneAnalytics) -> str:
    slippage_subquery = File("subquery_batchwise_internal_transfers.sql", path)
    token_list = get_trusted_tokens_from_url(
        HOSTED_ALLOWED_BUFFER_TRADING_TOKEN_LIST_URL)
    sql_query_for_allowed_token_list = generate_sql_query_for_allowed_token_list(
        token_list)
    slippage_query = dune.open_query(slippage_subquery.filename())
    return "\n".join(
        [
            slippage_query[0:5],
            sql_query_for_allowed_token_list,
            slippage_query[5:],
        ]
    )


def slippage_query(dune: DuneAnalytics) -> str:
    path = "./queries/slippage"
    select_slippage = File("select_slippage_results.sql", path)
    return "\n".join(
        [
            build_subquery(dune),
            dune.open_query(select_slippage.filename())
        ]
    )


def get_period_slippage(
        dune: DuneAnalytics,
        period_start: datetime,
        period_end: datetime,
) -> list:
    return dune.fetch(
        query_str=slippage_query(dune),
        network=Network.MAINNET,
        name='Slippage Accounting',
        parameters=[
            QueryParameter.date_type("StartTime", period_start),
            QueryParameter.date_type("EndTime", period_end),
            QueryParameter.text_type("TxHash", '0x'),
            QueryParameter.text_type("ResultTable", "results")
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch Accounting Period Totals")
    parser.add_argument(
        "--start",
        type=str,
        help="Accounting Period Start",
        required=True
    )
    parser.add_argument(
        "--end",
        type=str,
        help="Accounting Period End",
        required=True
    )
    args = parser.parse_args()

    dune_connection = DuneAnalytics.new_from_environment()

    slippage_for_period = get_period_slippage(
        dune=dune_connection,
        period_start=datetime.strptime(args.start, "%Y-%m-%d"),
        period_end=datetime.strptime(args.end, "%Y-%m-%d"),
    )

    pprint(slippage_for_period)
