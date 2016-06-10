import json

import requests
import grequests
from bs4 import BeautifulSoup as bs

from .point import Point


class AtlantParser(object):
    PARSER_NAME = "atlant"
    PARSER_URL = "http://telecom.by/internet/minsk/ethernet"
    STREET_SEARCH_URL = "http://telecom.by/at/zone/autocomplete/streets/2"

    def get_points(self):
        return []

    def _generate_search_url(self, l):
        return "/".join((self.STREET_SEARCH_URL, l))

    def get_street_names(self):
        """Obtain all streets with available internet connection"""
        street_names = []
        ltrs = "0123456789абвгдеёжзийклмнопрстуфхцчшщэюя"
        urls = (self._generate_search_url(l) for l in ltrs)

        # Asyncronous code causes some results not being returned by API
        # rs = (grequests.get(u) for u in urls)
        # results = grequests.map(rs)
        results = [requests.get(u) for u in urls]
        for i, r in enumerate(results):
            try:
                dict_data = r.json()
                street_names.extend(dict_data)
            except AttributeError:
                msg = "Error retrieving data for letter {}. ({})"
                print(msg.format(ltrs[i], self._generate_search_url(ltrs[i])))
        return street_names

    def get_house_list_for_street(self, street_name):
        pass


def main():
    parser = AtlantParser()
    # points = parser.get_points()
    streets = parser.get_street_names()
    print(streets)


if __name__ == '__main__':
    main()
