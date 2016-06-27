from collections import namedtuple


Connection = namedtuple('Connection', ["provider", "region", "city",
                                       "street", "house", "status"])
