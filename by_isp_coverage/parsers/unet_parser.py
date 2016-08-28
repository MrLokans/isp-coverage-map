import re

from bs4 import BeautifulSoup as bs
import grequests

from by_isp_coverage.parsers.base import BaseParser
from by_isp_coverage.connection import Connection
from by_isp_coverage.coordinate_obtainer import CoordinateObtainer
from by_isp_coverage.validators import ConnectionValidator

import logging

logging.getLogger("requests").setLevel(logging.WARNING)

STREET_ID_REGEX = r"this,\"(?P<_id>\d+)\""


class UNETParser(BaseParser):
    PARSER_NAME = "UNET"
    PARSER_URL = "http://unet.by"

    def __init__(self, coordinate_obtainer=None, validator=None):
        self.coordinate_obtainer = coordinate_obtainer
        self.validator = validator

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

        rs = (grequests.get(u, params={"act": "get_street_data",
                                       "data": n,
                                       "street": street_id})
              for n in nmbrs)
        results = grequests.map(rs)
        for resp in results:
            yield from self._houses_from_api_response(resp)

    def get_all_connected_streets(self):
        ltrs = "0123456789абвгдеёжзийклмнопрстуфхцчшщэюя"
        u = self.PARSER_URL

        rs = (grequests.get(u, params={"act": "get_street", "data": l})
              for l in ltrs)
        results = grequests.map(rs)
        for response in results:
            yield from self._street_tuples_from_response(response)

    def _street_tuples_from_response(self, resp):
        text = resp.text
        if not text:
            return []
        soup = bs(text, "html.parser")
        a_elems = soup.find_all("a")
        for a in a_elems:
            link_text = a.text.strip()
            onclick = a['onclick']
            _id = re.search(STREET_ID_REGEX, onclick).groupdict()['_id']
            yield (_id, link_text)

    def _houses_from_api_response(self, resp):
        text = resp.text
        if not text:
            return []
        soup = bs(text, "html.parser")
        return (a.text for a in soup.find_all("a"))

    def get_points(self):
        streets = self.get_all_connected_streets()
        street_data = [(s[1], list(self._house_list_for_street(s)))
                       for s in streets]
        return self.coordinate_obtainer.get_points(street_data)

    def __connections_from_street(self, street):
        region = "Минск"
        city = "Минск"
        status = "Есть подключение"
        for h in self._house_list_for_street(street):
            yield Connection(provider=self.PARSER_NAME, region=region,
                             city=city, street=street[1], status=status,
                             house=h)

    def get_connections(self, city="", street="", house_number=""):
        streets = self.get_all_connected_streets()
        for street in streets:
            connections = self.__connections_from_street(street)
            if self.validator:
                yield from self.validator.validate_connections(connections)
            else:
                yield from connections


if __name__ == '__main__':
    parser = UNETParser(coordinate_obtainer=CoordinateObtainer(),
                        validator=ConnectionValidator())
    # points = list(parser.get_points())
    for c in parser.get_connections():
        print(c)
