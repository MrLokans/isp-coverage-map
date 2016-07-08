class Connection(object):

    __slots__ = ('provider', 'region', 'city', 'street', 'house', 'status')

    def __init__(self, provider, region, city, street, house, status):
        self.provider = provider
        self.region = region
        self.city = city
        self.street = street
        self.house = house
        self.status = status

    @classmethod
    def from_modified_connection(cls, connection, **modified_fields):
        old_connection_dict = {s: getattr(connection, s)
                               for s in cls.__slots__}
        modified_fields_dict = {k: v for k, v in modified_fields.items()
                                if k in cls.__slots__}
        for k, v in modified_fields_dict.items():
            old_connection_dict[k] = v
        return cls(**old_connection_dict)

    def __repr__(self):
        s = "Connection({}, {}, {}, {}, {}, {})"
        return s.format(self.provider, self.region, self.city,
                        self.street, self.house, self.status)

    def __getitem__(self, attr):
        if attr not in self.__slots__:
            raise KeyError("Unknown item in connection: {}".format(attr))
        return getattr(self, attr)

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other_connection):
        return self.provider == other_connection.provider and\
               self.region == other_connection.region and\
               self.city == other_connection.city and\
               self.street == other_connection.street and\
               self.house == other_connection.house and\
               self.status == other_connection.status
