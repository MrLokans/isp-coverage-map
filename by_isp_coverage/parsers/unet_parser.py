import os
import re
import json

from lxml.html import fromstring
import grequests

from .base import BaseParser
from ..connection import Connection
from ..coordinate_obtainer import CoordinateObtainer


STREET_ID_REGEX = r"this,\"(?P<_id>\d+)\""


class UNETParser(BaseParser):
    PARSER_NAME = "UNET"
    PARSER_URL = "http://unet.by"

    def __init__(self, coordinate_obtainer):
        self.coordinate_obtainer = coordinate_obtainer

    def street_names_from_json(self, json_file):
        streets = []
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
            streets = [s["name"] for s in data["items"]]
            streets = [self._update_street_name(s) for s in streets]
        return streets

    def _update_street_name(self, street_name):
        """Moves words like 'street', 'crs' to the end of the name"""
        splitted = street_name.split(" ")
        if len(splitted) > 0 and splitted[0] == 'улица':
            splitted.pop(0)
        return " ".join(splitted)

    def _house_list_for_street(self, street):
        """Gets all house numbers if any on the street"""
        u = self.PARSER_URL
        street_id, _ = street
        nmbrs = range(1, 10)
        houses = []
        rs = (grequests.get(u, params={"act": "get_street_data",
                                       "data": n,
                                       "street": street_id})
              for n in nmbrs)
        results = grequests.map(rs)
        for resp in results:
            houses.extend(self._houses_from_api_response(resp))
        return houses

    def get_all_connected_streets(self):
        ltrs = "0123456789абвгдеёжзийклмнопрстуфхцчшщэюя"
        u = self.PARSER_URL

        streets = []
        rs = (grequests.get(u, params={"act": "get_street", "data": l})
              for l in ltrs)
        results = grequests.map(rs)
        for response in results:
            streets.extend(self._streets_from_api_response(response))
        streets = list(filter(lambda x: bool(x[1]), streets))
        return streets

    def _streets_from_api_response(self, resp):
        text = resp.text
        if not text:
            return ""
        results = []
        tree = fromstring(text)
        links = tree.xpath('//a')
        for link in links:
            link_text = link.text.strip()
            onclick = link.get('onclick')
            _id = re.search(STREET_ID_REGEX, onclick).groupdict()['_id']
            results.append((_id, link_text))
        return results

    def _houses_from_api_response(self, resp):
        text = resp.text
        if not text:
            return ""
        tree = fromstring(text)
        links = tree.xpath('//a/text()')
        return links

    def _read_cache_from_file(self,
                              cache_file="results.txt",
                              cache_splitter="|"):
        if not os.path.exists(cache_file):
            return {}
        cache = {}

        with open(cache_file, encoding="utf-8") as fp:
            for line in fp:
                search_str, point_part = line.split(cache_splitter)
                # Generally very bad idea
                cache[search_str] = eval(point_part)
        return cache

    def get_points(self, json_file=None):
        streets = self.get_all_connected_streets()
        street_data = [(s[1], self._house_list_for_street(s))
                       for s in streets]
        return self.coordinate_obtainer.get_points(street_data)

    def __connections_from_street(self, street):
        provider = "unet"
        region = u"Минск"
        city = u"Минск"
        status = u"Есть подключение"
        for h in self._house_list_for_street(street):
            yield Connection(provider=provider, region=region,
                             city=city, street=street, status=status,
                             house=h)

    def get_connections(self, city="", street="", house_number=""):
        streets = self.get_all_connected_streets()
        for street in streets:
            yield from self.__connections_from_street(street)


if __name__ == '__main__':
    parser = UNETParser(coordinate_obtainer=CoordinateObtainer())
    # points = list(parser.get_points())
    connections = list(parser.get_connections())
    # print(points)
    print(connections)
