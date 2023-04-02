from django.template.defaulttags import register


@register.filter
def get_item(d: dict, key: str):
    return d.get(key)


@register.filter
def getitem(d: dict, words: str):
    return d[words]


@register.filter
def concat(a, b):
    return str(a) + str(b)
