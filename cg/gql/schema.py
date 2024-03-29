import graphene

from gql.models import Asset, AssetExchange, Pool, Route
from graphene_django import DjangoObjectType


class AssetType(DjangoObjectType):
    class Meta:
        model = Asset
        fields = ("id", "symbol", "gecko_id")


class AssetExchangeType(DjangoObjectType):
    class Meta:
        model = AssetExchange
        fields = ("id", "from_asset", "to_asset", "route")


class PoolType(DjangoObjectType):
    geckoterminal_url = graphene.String()
    class Meta:
        model = Pool
        fields = ("id", "gecko_pool_id", "base_token", "quote_token", "address", "name", "network")

    def resolve_geckoterminal_url(self, info):
        return self.geckoterminal_url()

class RouteType(DjangoObjectType):
    class Meta:
        model = Route
        fields = ("id", "pool_from", "pool_to")

class Query(graphene.ObjectType):
    pools = graphene.List(PoolType)

    def resolve_pools(root, info):
        return Pool.objects.all()

    assets = graphene.List(AssetType)

    def resolve_assets(root, info):
        return Asset.objects.all()

    exchangeable_pair = graphene.List(AssetExchangeType)

    def resolve_exchangeable_pair(root, info):
        return AssetExchange.objects.all()

    routes = graphene.List(RouteType)

    def resolve_routes(root, info):
        return Route.objects.all()


schema = graphene.Schema(query=Query)
