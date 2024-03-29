from django.db import models
from django.db.models import ForeignKey


# Create your models here.

class Asset(models.Model):
    # asset_id = models.CharField(max_length=64)
    symbol = models.CharField(max_length=32)
    gecko_id = models.CharField(max_length=64)
    def __str__(self):
        return f"Asset [{self.id} - {self.symbol}]"

class Pool(models.Model):
    """ Static data for each pool """
    gecko_pool_id = models.CharField(max_length=64)
    base_token = models.CharField(max_length=64)
    quote_token = models.CharField(max_length=64)
    address = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    network = models.CharField(max_length=32)

    def geckoterminal_url(self):
        return f"https://www.geckoterminal.com/{self.network}/pools/{self.address}"


class Route(models.Model):
    pool_from = ForeignKey(Pool, on_delete=models.DO_NOTHING, related_name='%(class)s_from', null=True, blank=True)
    pool_to = ForeignKey(Pool, on_delete=models.DO_NOTHING, related_name='%(class)s_to', null=True, blank=True)


class AssetExchange(models.Model):
    from_asset = ForeignKey(Asset, on_delete=models.DO_NOTHING, related_name='%(class)s_from', null=True, blank=True)
    to_asset = ForeignKey(Asset, on_delete=models.DO_NOTHING, related_name='%(class)s_to', null=True, blank=True)
    route = ForeignKey(Route, on_delete=models.DO_NOTHING)
