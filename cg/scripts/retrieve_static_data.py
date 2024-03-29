import jsonpickle
import requests

from cg import settings
from cg.gql.reference import CGAPI

url = settings.config["COINGECKO_URL"]
headers = {settings.config["COINGECKO_API_HEADER"]: settings.config["COINGECKO_API_KEY"]}

def save_exchanges(exchanges):
    with open("static/exchanges.json", "w") as f:
        f.write(jsonpickle.dumps(exchanges))

def get_exchanges():
    more_exchanges = True
    per_page = 250
    page = 1
    all_exchanges = {}
    while more_exchanges:
        response = requests.get(url + CGAPI.exchanges+f"?per_page={per_page}&page={page}", headers=headers)
        print(response.text)
        j = response.json()
        more_exchanges = False
        for exchange in j:
            all_exchanges[exchange["id"]] = exchange
            more_exchanges = True
        page += 1

    save_exchanges(all_exchanges)

def run():
    get_exchanges()
