import json
from functools import reduce

# Attribution: https://gist.github.com/markhu/fbbab71359af00e527d0
class JsonOptions(dict):
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, payload):
        super().__init__()

        if isinstance(payload, str):
            payload = json.loads(payload)

        for name, value in payload.items():
            setattr(self, name, self._wrap(value))

    def __getattr__(self, attr: str):
        return self.attr(attr)

    def _wrap(self, value):
        if self._is_indexable(value):
            # (!) recursive (!)
            return type(value)([self._wrap(v) for v in value])
        elif isinstance(value, dict):
            return JsonOptions(value)
        else:
            return value

    def attr(self, attr: str, default=None):
        def _traverse(o, name):
            if o is None:
                return None

            if self._is_indexable(o):
                try:
                    return o[int(name)]
                except (IndexError, ValueError):
                    return None
            elif isinstance(o, dict):
                return o.get(name, None)
            else:
                return None

        if '.' in attr:
            value = reduce(_traverse, attr.split('.'), self)
        else:
            value = self.get(attr, None)

        return default if value is None else value

    @staticmethod
    def _is_indexable(o):
        return isinstance(o, (tuple, list, set, frozenset))
