import time

import grequests

from .base import BaseParser


STREET_ID_REGEX = r"this,\"(?P<_id>\d+)\""


class FlynetParser(BaseParser):
    PARSER_NAME = "flynet"
    PARSER_URL = "https://flynet.by"

    def __init__(self, coordinate_obtainer):
        self.coordinate_obtainer = coordinate_obtainer

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

    def get_points(self):
        streets = self.get_all_connected_streets()
        data = [{s: self._house_list_for_street(s)} for s in streets]
        return data


if __name__ == '__main__':
    parser = FlynetParser()
    points = parser.get_points()
    print(points)
