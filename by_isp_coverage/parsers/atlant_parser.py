import logging

import requests
import grequests
from bs4 import BeautifulSoup as bs

from .base import BaseParser
from ..coordinate_obtainer import CoordinateObtainer


logger = logging.getLogger(__name__)


class AtlantParser(BaseParser):
    PARSER_NAME = "atlant"
    PARSER_URL = "http://telecom.by"
    STREET_SEARCH_URL = "http://telecom.by/at/zone/autocomplete/streets/2"

    def __init__(self, coordinate_obtainer):
        self._session = requests.Session()
        self.coordinate_obtainer = coordinate_obtainer

    def get_points(self):
        street_names = self.get_street_names()
        houses_data = [(street_name, self.get_house_list_for_street(street_name))
                       for street_name in street_names]
        return self.coordinate_obtainer.get_points(houses_data)

    def get_connections(self, city="", street="", house_number=""):
        return []

    def _generate_search_url(self, l):
        return "/".join((self.STREET_SEARCH_URL, l))

    def _get_form_build_id(self):
        """Get form_build_id param value to make correct XHR requests"""
        page_content = requests.get("http://telecom.by/internet/minsk/ethernet").text
        soup = bs(page_content, "html.parser")
        selected = soup.select("form.zone__form input[name=\"form_build_id\"]")
        _id = selected[0]["value"]
        return _id

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
        results = []
        for u in urls:
            try:
                r = requests.get(u)
                results.append(r)
            except Exception:
                logger.exception("Error retrieving url {}".format(u))
        # results = [requests.get(u) for u in urls]
        for i, r in enumerate(results):
            try:
                dict_data = r.json()
                street_names.extend(dict_data)
            except AttributeError:
                letter = ltrs[i]
                msg = "Error retrieving data for letter {}. ({})"
                print(msg.format(letter, self._generate_search_url(letter)))
        return street_names

    def get_house_list_for_street(self, street_name):
        if not hasattr(self, "form_build_id"):
            self.form_build_id = self._get_form_build_id()

        data = {
            "street": street_name,
            "form_id": "at_zone_view_zone_form",
            "form_build_id": self.form_build_id,
        }
        try:
            r = self._session.post("http://telecom.by/system/ajax", data=data)
            json_ = r.json()
            houses_html = json_[1]["data"]
            house_numbers = self.__extract_houses(houses_html)
            return house_numbers.split(",")
        except Exception:
            logger.exception("Error occured getting house numbers.")
            return []


def main():
    parser = AtlantParser(CoordinateObtainer())
    points = list(parser.get_points())
    print(points)


if __name__ == '__main__':
    main()
