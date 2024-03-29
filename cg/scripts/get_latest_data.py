import collections
from collections import defaultdict
from dataclasses import dataclass
import json

import logging

import requests

logger = logging.getLogger(__name__)

from cg.utils.dotdict import JsonOptions
from gql.models import Pool, Asset, Route, AssetExchange

@dataclass
class ExchangeRate:
    # A unit of base_symbol will cost you base_token_price_native_currency of quote_symbols.
    # e.g. 1 WALLi will cost you approx 0.0(5)3923 SOL minus any txn fees.
    base_symbol: str
    quote_symbol: str
    base_token_price_native_currency: float
    pool_id: str

class Source(object):
    def get_json(self):
        raise NotImplementedError()
class FileSource(Source):
    def __init__(self, filename):
        self.filename = filename
    def get_json(self):
        return JsonOptions(json.load(open(self.filename,"r")))


class HTTPSource(Source):
    def __init__(self, url):
        self.url = url

    def get_json(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return JsonOptions(response.json())


sources = [
        # FileSource( "../.idea/httpRequests/2024-03-27T184048.200.json"),
        HTTPSource("https://api.geckoterminal.com/api/v2/networks/new_pools?include=base_token%2C%20quote_token%2C%20dex%2C%20network&page=1"),
        HTTPSource("https://api.geckoterminal.com/api/v2/networks/trending_pools?include=base_token%2C%20quote_token%2C%20dex%2C%20network&page=1"),
]

IGNORE_LIST = ["N/A"]

def should_ignore(symbol):
    return symbol in IGNORE_LIST

def save_asset_data(all_data_by_symbol):
    for asset in all_data_by_symbol:
        try:
            Asset.objects.get(symbol=asset)
        except Asset.DoesNotExist:
            a = Asset(
                symbol=asset,
                gecko_id=all_data_by_symbol[asset][0].relationships.base_token.data.id
            )
            logger.info("Creating asset {a}")
            a.save()

def get_or_create_route(pool_1, pool_2):
    try:
        route = Route.objects.get(pool_from=pool_1, pool_to=pool_2)
    except Route.DoesNotExist:
        route = Route(pool_from=pool_1, pool_to=pool_2)
        route.save()
        logger.info(f"Creating route {route}")
    return route

def get_or_create_asset_exchange(from_asset, to_asset, route):
    try:
        asset_exchange = AssetExchange.objects.get(from_asset=from_asset, to_asset=to_asset, route=route)
    except AssetExchange.DoesNotExist:
        asset_exchange = AssetExchange(from_asset=from_asset, to_asset=to_asset, route=route)
        asset_exchange.save()
    return asset_exchange



def save_exchange_matrix(exchange_matrix):
    for i in exchange_matrix:
        from_asset = Asset.objects.get(symbol=i)
        for j in exchange_matrix[i]:
            em_i_j = exchange_matrix[i][j]
            to_asset = Asset.objects.get(symbol=j)
            print(f"{from_asset} -> {to_asset}")
            number_of_routes = len(em_i_j[0])
            for k in range(number_of_routes):
                try:
                    p1 = em_i_j[0][k]
                    p2 = em_i_j[1][k]
                    pool_1 = Pool.objects.get(gecko_pool_id=p1.id)
                    pool_2 = Pool.objects.get(gecko_pool_id=p2.id)
                    route = get_or_create_route(pool_1, pool_2)
                    asset_exchange = get_or_create_asset_exchange(from_asset, to_asset, route)
                except IndexError:
                    print(f"Index error with {k}")





def save_pools(pools):
    for gecko_pool_id in pools:
        try:
            p = Pool.objects.get(gecko_pool_id = gecko_pool_id)
        except Pool.DoesNotExist:
            p = Pool(
                gecko_pool_id=gecko_pool_id,
                base_token=pools[gecko_pool_id].relationships.base_token.data.id,
                quote_token=pools[gecko_pool_id].relationships.quote_token.data.id,
                address=pools[gecko_pool_id].attributes.address,
                name=pools[gecko_pool_id].attributes.name,
                network=pools[gecko_pool_id].relationships.network.data.id,
            )
            p.save()

def run():
    fungibles = defaultdict(set)
    intersectors = defaultdict(set)

    all_data = {}
    all_data_by_symbol = defaultdict(list)
    all_relationships_by_id = dict()

    for source in sources:
        data = source.get_json()

        pools = {x["id"]:x for x in data["data"]}
        save_pools(pools)

        exchange_rates = []

        for pool_id in pools:
            market_data = pools[pool_id]
            tokens = {x.id:x for x in data.included}
            base_symbol = tokens[market_data.relationships.base_token.data.id].attributes.symbol
            if should_ignore(base_symbol):
                next
            quote_symbol = tokens[market_data.relationships.quote_token.data.id].attributes.symbol
            all_relationships_by_id[market_data.relationships.quote_token.data.id] = tokens[market_data.relationships.quote_token.data.id].attributes.symbol
            er = ExchangeRate(
                base_symbol,
                quote_symbol,
                market_data.attributes.base_token_price_native_currency,
                market_data.id
            )
            fungibles[quote_symbol].add(base_symbol)
            intersectors[base_symbol].add(quote_symbol)
            all_data[pool_id] = market_data
            all_data_by_symbol[base_symbol].append(market_data)
            exchange_rates.append(er)

        for er in exchange_rates:
            print(er)

    print(fungibles)
    intersector_filtered = [x for x in intersectors if len(intersectors[x]) > 1]
    print(intersector_filtered)
    if not intersector_filtered:
        print("No intersecting tokens :-(")

    # Now build matrix.
    # from token to token via pool_id at price xxx
    exchange_matrix = defaultdict(lambda: defaultdict(list))
    quote_tokens = [x for x in fungibles]
    for quote_token in quote_tokens:
        tokens = fungibles[quote_token]
        print(tokens)
        for i in tokens:
            for j in tokens:
                if i != j:
                    exchange_matrix[i][j] = (
                        # This is so we can keep all routes from i to j if there are multiple pools that can be used to exchange
                        # Unfortunately, as of now the datasets do not have multiple paths from one token to another.
                            [x for x in all_data_by_symbol[i] if all_relationships_by_id[x.relationships.quote_token.data.id] == quote_token],
                            [x for x in all_data_by_symbol[j] if all_relationships_by_id[x.relationships.quote_token.data.id] == quote_token],
                            quote_token,
                    )
    save_asset_data(all_data_by_symbol)
    save_exchange_matrix(exchange_matrix)


def get_example(exchange_matrix):
    mew_to_slerf = exchange_matrix["MEW"]["SLERF"]
    example_exchange = (mew_to_slerf[0][0], mew_to_slerf[1][0])
    rate_mew_to_sol = float(example_exchange[0].attributes.base_token_price_native_currency)
    rate_slerf_to_sol = float(example_exchange[1].attributes.base_token_price_native_currency)
    # 1 Mew will cost you this many SLERF
    rate_mew_to_slerf = rate_mew_to_sol / rate_slerf_to_sol
    print(f"1 MEW will cost you {rate_mew_to_slerf} SLERF via {mew_to_slerf[2]}")


if __name__ == '__main__':
    run()
