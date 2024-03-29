### Mini CG -> Graph QL Project

The service runs using django as a holding platform as that gives us easy integration with a graphql service (via django-graphene), database connectivity (for storage), various options on caching (redis, in memory etc).

Once started, the docker container will refresh data once per minute from both the trending and latest pools data.

It then generates a very basic graph of which token can be exchanged for another token via the pools.

Unfortunately, there are not many edges to the graph, so I didn't end up writing the "best route" part as there were never multiple routes.

The structures I've used can be seen in `cg/gql/models.py` and the graphql implementations of them were done very simply in  `cg/gql/schema.py`. I added the `geckoterminal_url` as an example as to how to add computed elements.


### How to run (in order of decreasing simplicity)
1) Just use the link https://coingeckodemo.reneo.io/graphql (I've left an instance running for now)
2) Use docker. Navigate to the docker directory and read the README.md there
3) Local Python
   1) Install a version of python 3.12. 
   2) Install the requirements from the requirements.txt file
   3) Execute `python manage.py runserver 0.0.0.0:8000` in the `cg` directory
   4) While running the above, from time to run, execute `python manage.py runscript scripts.get_latest_data` to get an updated dataset

### Data storage
I'm just using the default database for django apps right now - you can see that in `cg\db.sqlite3`

### Ease of scaling

It's very simple to scale just by increasing the number of web servers. A faster in memory database could be used.

### Working GQL queries

The following are working queries

#### Gets the graph of all exchangeable assets
```
query ExchangablePair {
  exchangeablePair {
    fromAsset {
      symbol
      geckoId
    }
    toAsset {
      symbol
      geckoId
    }
    route {
      poolFrom {
        name
      }
      poolTo {
        name
      }
    }
}
}
```

#### All Assets
```
query Assets {
  assets {
  symbol
  geckoId
}
}
```

#### All Pools
```
query Pool {
  pools {
    geckoPoolId
    baseToken
    quoteToken
    address
    name
    network
    geckoterminalUrl
  }
}
```

#### All 'routes' 
```
query Route {
  routes {
    poolFrom {
      id
      network
      name
    }
    poolTo {
      id
      network
      name
    }
  }
}

```


### Caching
Very basic use of database in order to provide data to graphene
Servers can be spun up on heavy load easily. 
Even further caching can be done by an instance of redis
Done via django's internal caching mechanism is infrastructure configurable.
However, graphql queries are POST

There's a mini example of how to get a rate from one token to another in `get_latest_data.py\get_example()`

### General notes.

Looking at the actual data, there is very few options to optimise swaps. AFAIK liquidity pools don't have a bid/offer spread as per normal currency exchanges, this is all implicit in the pool itself. Therefore, one would always use which ever has the lowest margin.

API Keys weren't required but there is provision for them.

Pagination of queries wasn't required as there wasn't a lot of data returned.
