import time

import grequests

from .base import BaseParser
from ..connection import Connection


STREET_ID_REGEX = r"this,\"(?P<_id>\d+)\""


class FlynetParser(BaseParser):
    PARSER_NAME = "flynet"
    PARSER_URL = "https://flynet.by"

    def __init__(self, coordinate_obtainer=None, validator=None):
        self.coordinate_obtainer = coordinate_obtainer
        self.validator = validator

    def get_all_connected_streets(self):
        ltrs = "0123456789абвгдеёжзийклмнопрстуфхцчшщэюя"
        streets = set()
        u = self.PARSER_URL + '/connection/searcher.php'

        rs = (grequests.get(u, params={"what": "str",
                                       "limit": 1500,
                                       "timestamp": int(time.time()),
                                       "street": l,
                                       "q": 1,
                                       })
              for l in ltrs)
        results = grequests.map(rs)

        for response in results:
            streets.update(self._streets_from_api_response(response))

        streets.discard('')
        return streets

    def _streets_from_api_response(self, resp):
        text = resp.text
        if not text:
            return ""
        streets = text.split('\n')
        results = {s.split('|')[0] for s in streets}
        return results

    def _houses_from_api_response(self, resp):
        text = resp.text
        if not text:
            return ""

        houses = text.split('\n')
        results = {h.split('|')[0] for h in houses}
        return results

    def _house_list_for_street(self, street):
        numbers = list(range(1, 10))
        house_numbers = set()
        u = self.PARSER_URL + '/connection/searcher.php'
        rs = (grequests.get(u, params={"what": "house",
                                       "limit": 1500,
                                       "timestamp": int(time.time()),
                                       "street": street,
                                       "q": n,
                                       })
              for n in numbers)
        results = grequests.map(rs)
        for response in results:
            house_numbers.update(self._houses_from_api_response(response))
        house_numbers.discard('')
        return house_numbers

    def __connections_from_street(self, street):
        region = u"Минск"
        city = u"Минск"
        status = u"Есть подключение"
        for h in self._house_list_for_street(street):
            yield Connection(provider=self.PARSER_NAME, region=region,
                             city=city, street=street, status=status,
                             house=h)

    def get_connections(self):
        streets = self.get_all_connected_streets()
        for street in streets:
            connections = self.__connections_from_street(street)
            if self.validator:
                yield from self.validator.validate_connections(connections)
            else:
                yield from connections

    def get_points(self):
        streets = self.get_all_connected_streets()
        data = [(s, self._house_list_for_street(s)) for s in streets]
        return self.coordinate_obtainer.get_points(data)


if __name__ == '__main__':
    from ..coordinate_obtainer import CoordinateObtainer
    parser = FlynetParser(CoordinateObtainer())
    # points = parser.get_points()
    # print(points)
    # print(list(parser.get_connections()))
    print(list(parser.get_points()))
