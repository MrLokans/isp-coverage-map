import json

import requests
import grequests
from bs4 import BeautifulSoup as bs

from .base import BaseParser
from .point import Point


class AtlantParser(BaseParser):
    PARSER_NAME = "atlant"
    PARSER_URL = "http://telecom.by/internet/minsk/ethernet"
    STREET_SEARCH_URL = "http://telecom.by/at/zone/autocomplete/streets/2"

    def __init__(self):
        self._session = requests.Session()

    def get_points(self):
        return []

    def _generate_search_url(self, l):
        return "/".join((self.STREET_SEARCH_URL, l))

    def _get_form_build_id(self):
        """Get form_build_id param value to make correct XHR requests"""
        page_content = self._session.get(self.PARSER_URL).text
        soup = bs(page_content, "html.parser")
        # It does not work for some reason, may be we should set custom user-agent
        input_ = soup.find(name="input", attrs={"name": "form_build_id"})
        return input_["value"]

    def __extract_houses(self, text):
        soup = bs(text, "html.parser")
        div_ = soup.find(name="div", attrs={"class": "zone__buildings"})
        return div_.text

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
        if not hasattr(self, "form_build_id"):
            self.form_build_id = self._get_form_build_id()

        data = {
            "street": "Янковского",
            "form_id": "at_zone_view_zone_form",
            "form_build_id": self.form_build_id,
        }
        r = self._session.post("http://telecom.by/system/ajax", data=data)
        json_ = r.json()
        houses_html = json_[1]["data"]
        house_numbers = self.__extract_houses(houses_html)
        return house_numbers.split(",")


def main():
    parser = AtlantParser()
    # points = parser.get_points()
    # streets = parser.get_street_names()
    houses = parser.get_house_list_for_street("TEST")
    print(houses)


if __name__ == '__main__':
    main()
